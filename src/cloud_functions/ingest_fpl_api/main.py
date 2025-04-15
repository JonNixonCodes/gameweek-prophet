import functions_framework
import requests
import pandas as pd
from google.cloud import storage
from datetime import datetime
import logging
import os
import tempfile

def setup_logging():
    """Sets up logging configuration."""
    logging.basicConfig(
        format='%(asctime)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )

def fetch_fpl_data(endpoint):
    """Fetches data from the FPL API.

    Args:
        endpoint (str): The API endpoint to fetch.

    Returns:
        dict: The JSON response from the API.
    """
    base_url = "https://fantasy.premierleague.com/api/"
    url = base_url + endpoint
    try:
        logging.info(f"Fetching data from {endpoint}")
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching data from {endpoint}: {e}")
        raise

def save_df_to_gcs(bucket_name, data, file_path, source_date):
    """Saves a pandas DataFrame to Google Cloud Storage as a Parquet file with Hive partitioning.

    Args:
        bucket_name (str): The name of the GCS bucket.
        data (pd.DataFrame): The DataFrame to save.
        file_path (str): The base path within the bucket to save the file (e.g., "raw/fpl_api/elements/").
        source_date (str): The source date for Hive partitioning (YYYY-MM-DD).
    """
    try:
        # Initialize GCS client
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        
        # Verify bucket exists
        if not bucket.exists():
            raise ValueError(f"Bucket {bucket_name} does not exist")

        # Add the Hive partition directory to the file path
        full_file_path = f"{file_path}source_date={source_date}/data.parquet"
        blob = bucket.blob(full_file_path)

        # First save the dataframe to a local parquet file
        temp_parquet_file = f"{tempfile.gettempdir()}/temp{datetime.now().strftime('%Y%m%d%H%M%S')}.parquet"
        data.to_parquet(temp_parquet_file)

        # Upload the file
        blob.upload_from_filename(temp_parquet_file)

        logging.info(f"Successfully saved data to gs://{bucket_name}/{full_file_path}")
        return True
    except Exception as e:
        logging.error(f"Error saving data to GCS: {e}")
        raise

@functions_framework.http
def ingest_fpl_api(request):
    """
    Main entry point for Google Cloud Function to ingest data from the FPL API and save it to Google Cloud Storage.
    
    Args:
        request (flask.Request, optional): The request object from functions-framework.
        
    Returns:
        dict: A dictionary containing the status of the function execution.
    """
    # Set up logging
    setup_logging()

    try:
        logging.info("Starting data ingestion")
        source_date = datetime.now().strftime("%Y-%m-%d")

        # Get bucket name from environment variable, use default if not set
        bucket_name = os.environ.get("BUCKET_NAME", "leverageai-sandbox-data")
        logging.info(f"Bucket name: {bucket_name}")

        # Fetch data from various endpoints
        bootstrap_data = fetch_fpl_data("bootstrap-static/")
        elements_data = bootstrap_data['elements']
        teams_data = bootstrap_data['teams']

        # Convert to Pandas DataFrames
        elements_df = pd.DataFrame(elements_data)
        teams_df = pd.DataFrame(teams_data)

        # Fetch player summary data
        player_summary_data = {}
        for player_id in elements_df['id']:
            player_summary_data[player_id] = fetch_fpl_data(f"element-summary/{player_id}/")

        # Extract history from player summary data
        player_history_data = {}
        for player_id, data in player_summary_data.items():
            player_history_data[player_id] = data['history']

        # Convert player history to a DataFrame
        player_history_dfs = []
        for player_id, history in player_history_data.items():
            temp_df = pd.DataFrame(history)
            temp_df['element'] = player_id  # Add player ID as a column
            player_history_dfs.append(temp_df)

        player_history_df = pd.concat(player_history_dfs, ignore_index=True)

        # Fetch fixture data
        fixture_data = {}
        for team_id in teams_df['id']:
            fixture_data[team_id] = fetch_fpl_data(f"fixtures/?team={team_id}")

        # Extract fixture data from team fixture data
        fixtures_dfs = []
        for team_id, fixtures in fixture_data.items():
            temp_df = pd.DataFrame(fixtures)
            temp_df['team_id'] = team_id
            fixtures_dfs.append(temp_df)

        fixtures_df = pd.concat(fixtures_dfs, ignore_index=True)

        # Save DataFrames to GCS as Parquet files with Hive partitioning
        save_df_to_gcs(bucket_name, elements_df, "raw/fpl_api/elements/", source_date)
        save_df_to_gcs(bucket_name, teams_df, "raw/fpl_api/teams/", source_date)
        save_df_to_gcs(bucket_name, player_history_df, "raw/fpl_api/player_history/", source_date)
        save_df_to_gcs(bucket_name, fixtures_df, "raw/fpl_api/fixtures/", source_date)

        logging.info("Data ingestion complete")
        return {"status": "success"}

    except Exception as e:
        logging.error(f"Error during data ingestion: {e}")
        raise


if __name__ == "__main__":
    ingest_fpl_api()
    