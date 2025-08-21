import argparse
import json
from datetime import datetime

from google.cloud import storage
from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col,
    concat,
    lit,
    when,
    sum,
    max,
    count
)
from pyspark.sql.window import Window
from functools import reduce
from pyspark.sql import DataFrame
from pyspark.sql.types import (
    BooleanType,
    DateType,
    FloatType,
    IntegerType,
    StringType,
    StructField,
    StructType,
    TimestampType,
)


def json_to_spark_schema(schema_json):
    """Converts a JSON schema to a Spark StructType."""
    type_mapping = {
        "string": StringType(),
        "integer": IntegerType(),
        "float": FloatType(),
        "boolean": BooleanType(),
        "timestamp": TimestampType(),
        "date": DateType()
    }
    fields = [StructField(field["name"], type_mapping[field["type"]], field.get("nullable", True)) for field in schema_json]
    return StructType(fields)


def add_metadata_from_config(df, metadata):
    """Adds season_code and source_date from the config."""
    df = df.withColumn("season_code", lit(metadata["season_code"]))
    df = df.withColumn("source_date", lit(datetime.fromisoformat(metadata["source_date"])))
    return df


def load_data(spark, config):
    """Loads data from GCS based on the provided configuration."""
    dataframes = {}
    for name, input_config in config["inputs"].items():
        format = input_config["format"]
        if format == "csv":
            schema = json_to_spark_schema(input_config["schema"])
            df = spark.read.format(input_config["format"]) \
                .option("header", "true") \
                .schema(schema) \
                .load(input_config["path"])
        elif format == "parquet":
            df = spark.read.format(input_config["format"]) \
                .load(input_config["path"])
        else:
            raise ValueError(f"Unsupported format: {format}")
        df = add_metadata_from_config(df, input_config["metadata"])
        dataframes[name] = df
    return dataframes


def prepare_player_data(dataframes):
    """Prepares the player data by transforming historical, current, and future player data, and then unioning them together."""
    # Union historical dataframes
    historical_merged_gw_df = reduce(lambda df1, df2: df1.unionByName(df2, allowMissingColumns=True), [df for key, df in dataframes.items() if key.startswith("historical_merged_gw")])
    historical_players_raw_df = reduce(lambda df1, df2: df1.unionByName(df2, allowMissingColumns=True), [df for key, df in dataframes.items() if key.startswith("historical_players_raw")])
    historical_teams_df = reduce(lambda df1, df2: df1.unionByName(df2, allowMissingColumns=True), [df for key, df in dataframes.items() if key.startswith("historical_teams")])
    historical_fixtures_df = reduce(lambda df1, df2: df1.unionByName(df2, allowMissingColumns=True), [df for key, df in dataframes.items() if key.startswith("historical_fixtures")])

    # Historical player data
    historical_player_data = historical_merged_gw_df \
        .withColumnRenamed("element", "player_id") \
        .withColumnRenamed("team", "team_name") \
        .withColumnRenamed("opponent_team", "opponent_team_id") \
        .withColumnRenamed("fixture", "fixture_id")

    historical_players_unique = historical_players_raw_df \
        .select("id", "code", "first_name", "second_name", "season_code") \
        .withColumnRenamed("id", "player_id") \
        .withColumnRenamed("code", "player_code") \
        .distinct()

    historical_teams_unique = historical_teams_df \
        .select("id", "code", "name", "season_code") \
        .withColumnRenamed("id", "team_id") \
        .withColumnRenamed("code", "team_code") \
        .withColumnRenamed("name", "team_name") \
        .distinct()

    historical_opponent_teams_unique = historical_teams_df \
        .select("id", "code", "name", "season_code") \
        .withColumnRenamed("id", "opponent_team_id") \
        .withColumnRenamed("code", "opponent_team_code") \
        .withColumnRenamed("name", "opponent_team_name") \
        .distinct()

    historical_fixtures_unique = historical_fixtures_df \
        .select("id", "code", "season_code") \
        .withColumnRenamed("id", "fixture_id") \
        .withColumnRenamed("code", "fixture_code") \
        .distinct()

    historical_player_data = historical_player_data \
        .join(historical_players_unique, ["player_id", "season_code"], "inner") \
        .join(historical_teams_unique, ["team_name", "season_code"], "inner") \
        .join(historical_opponent_teams_unique, ["opponent_team_id", "season_code"], "inner") \
        .join(historical_fixtures_unique, ["fixture_id", "season_code"], "inner")

    player_data_columns = [
        "player_name", "player_code", "team_name", "team_code",
        "opponent_team_name", "opponent_team_code", "position", "kickoff_time",
        "gameweek", "round", "fixture_code", "season_code", "goals_scored",
        "goals_conceded", "assists", "expected_assists",
        "expected_goal_involvements", "expected_goals",
        "expected_goals_conceded", "penalties_missed", "penalties_saved",
        "saves", "bps", "minutes", "yellow_cards", "red_cards", "own_goals",
        "starts", "was_home", "influence", "creativity", "threat",
        "ict_index", "clean_sheets", "total_points",
    ]

    cleaned_historical_player_data = historical_player_data \
        .withColumnRenamed("name", "player_name") \
        .withColumnRenamed("GW", "gameweek") \
        .select(player_data_columns)


    # Current player data
    current_player_data = dataframes["api_player_history"] \
        .withColumnRenamed("element", "player_id") \
        .withColumnRenamed("fixture", "fixture_id") \
        .withColumnRenamed("opponent_team", "opponent_team_id")

    current_fixtures_unique = dataframes["api_fixtures"] \
        .select("id", "code", "team_a", "team_h", "event", "season_code") \
        .withColumnRenamed("id", "fixture_id") \
        .withColumnRenamed("code", "fixture_code") \
        .withColumnRenamed("team_a", "away_team_id") \
        .withColumnRenamed("team_h", "home_team_id") \
        .withColumnRenamed("event", "gameweek") \
        .distinct()

    current_players_unique = dataframes["api_elements"] \
        .select("id", "code", "element_type", "first_name", "second_name", "season_code") \
        .withColumnRenamed("id", "player_id") \
        .withColumnRenamed("code", "player_code") \
        .distinct()

    current_teams_unique = dataframes["api_teams"] \
        .select("id", "code", "name", "season_code") \
        .withColumnRenamed("id", "team_id") \
        .withColumnRenamed("code", "team_code") \
        .withColumnRenamed("name", "team_name") \
        .distinct()

    current_opponent_teams_unique = dataframes["api_teams"] \
        .select("id", "code", "name", "season_code") \
        .withColumnRenamed("id", "opponent_team_id") \
        .withColumnRenamed("code", "opponent_team_code") \
        .withColumnRenamed("name", "opponent_team_name") \
        .distinct()

    current_player_data = current_player_data \
        .join(current_players_unique, ["player_id", "season_code"], "inner") \
        .join(current_fixtures_unique, ["fixture_id", "season_code"], "inner") \
        .withColumn("team_id", when(col("was_home") == True, col("home_team_id")).otherwise(col("away_team_id"))) \
        .join(current_teams_unique, ["team_id", "season_code"], "inner") \
        .join(current_opponent_teams_unique, ["opponent_team_id", "season_code"], "inner")

    cleaned_current_player_data = current_player_data \
        .withColumn("player_name", concat(col("first_name"), lit(" "), col("second_name"))) \
        .withColumn("position",
                    when(col("element_type") == 1, "GK") \
                    .when(col("element_type") == 2, "DEF") \
                    .when(col("element_type") == 3, "MID") \
                    .when(col("element_type") == 4, "FWD")) \
        .select(player_data_columns)

    # Future player data
    current_player_unique = dataframes["api_elements"] \
        .select("id", "code", "team", "team_code", "element_type", "first_name", "second_name", "season_code") \
        .withColumnRenamed("id", "player_id") \
        .withColumnRenamed("code", "player_code") \
        .withColumnRenamed("team", "team_id") \
        .distinct()

    current_home_fixtures_unique = dataframes["api_fixtures"] \
        .select("id", "code", "kickoff_time", "team_a", "team_h", "event", "season_code") \
        .withColumnRenamed("id", "fixture_id") \
        .withColumnRenamed("code", "fixture_code") \
        .withColumnRenamed("team_h", "team_id") \
        .withColumnRenamed("team_a", "opponent_team_id") \
        .withColumnRenamed("event", "gameweek") \
        .withColumn("was_home", lit(True)) \
        .distinct()

    current_away_fixtures_unique = dataframes["api_fixtures"] \
        .select("id", "code", "kickoff_time", "team_a", "team_h", "event", "season_code") \
        .withColumnRenamed("id", "fixture_id") \
        .withColumnRenamed("code", "fixture_code") \
        .withColumnRenamed("team_a", "team_id") \
        .withColumnRenamed("team_h", "opponent_team_id") \
        .withColumnRenamed("event", "gameweek") \
        .withColumn("was_home", lit(False)) \
        .distinct()

    current_fixtures_unique = current_home_fixtures_unique.unionByName(current_away_fixtures_unique)
    
    current_fixtures = current_player_data.select("fixture_code").distinct()

    future_player_data = current_player_unique \
        .join(current_fixtures_unique, ["team_id", "season_code"], "inner") \
        .join(current_teams_unique, ["team_id", "team_code", "season_code"], "inner") \
        .join(current_opponent_teams_unique, ["opponent_team_id", "season_code"], "inner") \
        .join(current_fixtures, ["fixture_code"], "left_anti")

    cleaned_future_player_data = future_player_data \
        .withColumn("player_name", concat(col("first_name"), lit(" "), col("second_name"))) \
        .withColumn("position",
                    when(col("element_type") == 1, "GK")
                    .when(col("element_type") == 2, "DEF")
                    .when(col("element_type") == 3, "MID")
                    .when(col("element_type") == 4, "FWD")) \
        .withColumn("round", col("gameweek"))
    
    future_player_data_cols = [c for c in player_data_columns if c in cleaned_future_player_data.columns]
    cleaned_future_player_data = cleaned_future_player_data.select(future_player_data_cols)

    # Union all data
    player_data = cleaned_historical_player_data \
        .union(cleaned_current_player_data) \
        .unionByName(cleaned_future_player_data, allowMissingColumns=True)

    return player_data

def prepare_team_data(player_data):
    """Prepares the team data by aggregating player data."""
    team_data_keys = [
        "fixture_code",
        "team_code",
        "opponent_team_code",
        "kickoff_time",
        "season_code"
    ]

    team_data = player_data \
        .groupBy(team_data_keys) \
        .agg(
            sum("goals_scored").alias("team_goals_scored"),
            max("goals_conceded").alias("team_goals_conceded"),
            sum("assists").alias("team_assists"),
            sum("expected_assists").alias("team_expected_assists"),
            sum("expected_goal_involvements").alias("team_expected_goal_involvements"),
            sum("expected_goals").alias("team_expected_goals"),
            max("expected_goals_conceded").alias("team_expected_goals_conceded"),
            sum("penalties_missed").alias("team_penalties_missed"),
            sum("penalties_saved").alias("team_penalties_saved"),
            sum("saves").alias("team_saves"),
            sum("bps").alias("team_bps"),
            sum("total_points").alias("team_total_points"),
            sum("yellow_cards").alias("team_yellow_cards"),
            sum("red_cards").alias("team_red_cards"),
            sum("own_goals").alias("team_own_goals"),
            max("clean_sheets").alias("team_clean_sheets"),
        )

    team_data_columns = [
        "team_code",
        "opponent_team_code",
        "fixture_code",
        "kickoff_time",
        "season_code",
        "team_goals_scored",
        "team_goals_conceded",
        "team_assists",
        "team_expected_assists",
        "team_expected_goal_involvements",
        "team_expected_goals",
        "team_expected_goals_conceded",
        "team_penalties_missed",
        "team_penalties_saved",
        "team_saves",
        "team_bps",
        "team_yellow_cards",
        "team_red_cards",
        "team_own_goals",
        "team_clean_sheets",
        "team_total_points",
    ]

    team_data = team_data.select(team_data_columns)
    return team_data, team_data_keys

def feature_engineering(player_data, team_data, team_data_keys):
    """Performs feature engineering on the player and team data."""
    # 5.1 Build Player Features
    recent_window = Window.partitionBy("player_code").orderBy("kickoff_time").rowsBetween(Window.currentRow - 4, Window.currentRow - 1)
    long_term_window = Window.partitionBy("player_code").orderBy("kickoff_time").rowsBetween(Window.currentRow - 12, Window.currentRow - 5)
    metrics = [
        "goals_scored", "goals_conceded", "assists", "expected_assists",
        "expected_goal_involvements", "expected_goals", "expected_goals_conceded",
        "penalties_missed", "penalties_saved", "saves", "bps", "minutes",
        "yellow_cards", "red_cards", "own_goals", "starts", "influence",
        "creativity", "threat", "ict_index", "clean_sheets", "total_points",
    ]
    player_features = player_data
    for metric in metrics:
        player_features = player_features.withColumn(
            f"recent_{metric}",
            when(
                (count(lit(1)).over(recent_window) >= 4) &
                (count(col(metric)).over(recent_window) == count(lit(1)).over(recent_window)),
                sum(col(metric)).over(recent_window)
            ).otherwise(None)
        )
        player_features = player_features.withColumn(
            f"long_term_{metric}",
            when(
                (count(lit(1)).over(long_term_window) >= 8) &
                (count(col(metric)).over(long_term_window) == count(lit(1)).over(long_term_window)),
                sum(col(metric)).over(long_term_window)
            ).otherwise(None)
        )

    # 5.2 Build Team Features
    recent_window = Window.partitionBy("team_code").orderBy("kickoff_time").rowsBetween(Window.currentRow - 4, Window.currentRow - 1)
    long_term_window = Window.partitionBy("team_code").orderBy("kickoff_time").rowsBetween(Window.currentRow - 12, Window.currentRow - 5)
    metrics = [
        "team_goals_scored", "team_goals_conceded", "team_assists",
        "team_expected_assists", "team_expected_goal_involvements",
        "team_expected_goals", "team_expected_goals_conceded",
        "team_penalties_missed", "team_penalties_saved", "team_saves", "team_bps",
        "team_yellow_cards", "team_red_cards", "team_own_goals",
        "team_clean_sheets", "team_total_points",
    ]
    team_features = team_data
    for metric in metrics:
        team_features = team_features.withColumn(
            f"recent_{metric}",
            when(
                (count(lit(1)).over(recent_window) >= 4) &
                (count(col(metric)).over(recent_window) == count(lit(1)).over(recent_window)),
                sum(col(metric)).over(recent_window)
            ).otherwise(None)
        )
        team_features = team_features.withColumn(
            f"long_term_{metric}",
            when(
                (count(lit(1)).over(long_term_window) >= 8) &
                (count(col(metric)).over(long_term_window) == count(lit(1)).over(long_term_window)),
                sum(col(metric)).over(long_term_window)
            ).otherwise(None)
        )

    # 5.3 Merge Features
    features = player_features.join(team_features, team_data_keys, "inner")

    # 5.4 Transform Categorical Features
    features = features \
        .withColumn("position_GK", when(col("position") == "GK", 1).otherwise(0)) \
        .withColumn("position_DEF", when(col("position") == "DEF", 1).otherwise(0)) \
        .withColumn("position_MID", when(col("position") == "MID", 1).otherwise(0)) \
        .withColumn("position_FWD", when(col("position") == "FWD", 1).otherwise(0))
    features = features \
        .withColumn("was_home_true", when(col("was_home") == True, 1).otherwise(0)) \
        .withColumn("was_home_false", when(col("was_home") == False, 1).otherwise(0))

    return features

def main(args):
    """Main function for the ETL job."""
    # Initialize Spark session
    spark = SparkSession.builder.appName("gameweek-prophet-etl").getOrCreate()

    # # Read config file from GCS
    # storage_client = storage.Client()
    # bucket_name, blob_name = args.job_config.replace("gs://", "").split("/", 1)
    # bucket = storage_client.bucket(bucket_name)
    # blob = bucket.blob(blob_name)
    # config_str = blob.download_as_text()
    # config = json.loads(config_str)

    # Read config file from local storage
    with open(args.job_config, "r") as file:
        config = json.load(file)

    # Load data
    dataframes = load_data(spark, config)

    # Prepare player and team data
    player_data = prepare_player_data(dataframes)
    team_data, team_data_keys = prepare_team_data(player_data)

    # Feature engineering
    features = feature_engineering(player_data, team_data, team_data_keys)

    # Write output
    output_config = config["output"]
    features.write.format(output_config["format"]) \
        .mode(output_config["mode"]) \
        .parquet(output_config["path"])


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--job-config", required=True)
    args = parser.parse_args()
    main(args)
