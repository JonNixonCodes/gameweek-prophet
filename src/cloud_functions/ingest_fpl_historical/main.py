import functions_framework
import requests
from google.cloud import storage
from datetime import datetime
import logging
import os

def setup_logging():
    """Sets up logging configuration."""
    logging.basicConfig(
        format='%(asctime)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )

def fetch_fpl_historical_data(base_url, season_year):
    """Fetches historical FPL data from the GitHub repository.

    Args:
        base_url (str): The base URL for the data, with a placeholder for season_year.
        season_year (str): The season year in format YYYY-YY (e.g., "2022-23").

    Returns:
        tuple: A tuple containing the raw CSV data as a string and the source URL.
    """
    url = base_url.format(season_year=season_year)
    try:
        logging.info(f"Fetching data for {season_year} from {url}...")
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes
        
        logging.info(f"Successfully fetched data for {season_year}")
        return response.text, url
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching data for {season_year}: {e}")
        raise

def save_csv_to_gcs(bucket_name, csv_data, file_path, source_date, season_year, source_url):
    """Saves raw CSV data to Google Cloud Storage with Hive partitioning.

    Args:
        bucket_name (str): The name of the GCS bucket.
        csv_data (str): The raw CSV data to save.
        file_path (str): The base path within the bucket to save the file (e.g., "raw/fpl_historical/merged_gw/").
        source_date (str): The source date for Hive partitioning (YYYY-MM-DD).
        season_year (str): The season year of the data (e.g., "2022-23").
        source_url (str): The URL the data was fetched from.
    """
    try:
        # Initialize GCS client
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        
        # Verify bucket exists
        if not bucket.exists():
            raise ValueError(f"Bucket {bucket_name} does not exist")

        # Add the Hive partition directory to the file path
        full_file_path = f"{file_path}source_date={source_date}/data.csv"
        blob = bucket.blob(full_file_path)

        # Set metadata
        blob.metadata = {
            'season_year': season_year,
            'source_url': source_url,
            'source_date': source_date
        }

        # Upload the raw CSV data
        blob.upload_from_string(csv_data, content_type='text/csv')

        logging.info(f"Successfully saved data to gs://{bucket_name}/{full_file_path}")
        return True
    except Exception as e:
        logging.error(f"Error saving data to GCS: {e}")
        raise

@functions_framework.http
def ingest_fpl_historical(request):
    """
    Main entry point for Google Cloud Function to ingest historical data from the FPL GitHub repo and save it to GCS.
    
    Args:
        request (flask.Request): The request object.
            Query parameters:
            start_year (int): The starting year of the season (e.g., 2022). Defaults to 3 years ago.
            end_year (int): The ending year of the season (e.g., 2024). Defaults to the current year + 1.
        
    Returns:
        dict: A dictionary containing the status of the function execution.
    """
    # Set up logging
    setup_logging()

    try:
        logging.info("Starting historical data ingestion")
        source_date = datetime.now().strftime("%Y-%m-%d")

        # Get bucket name from environment variable, use default if not set
        bucket_name = os.environ.get("BUCKET_NAME", "leverageai-sandbox-data")
        logging.info(f"Bucket name: {bucket_name}")

        # Get year range from request arguments or use defaults
        current_year = datetime.now().year
        start_year_arg = request.args.get('start_year', current_year - 3)
        end_year_arg = request.args.get('end_year', current_year + 1)
        start_year = int(start_year_arg)
        end_year = int(end_year_arg)
        
        logging.info(f"Processing seasons from {start_year} to {end_year-1}")

        datasets = {
            "merged_gw": "https://raw.githubusercontent.com/vaastav/Fantasy-Premier-League/master/data/{season_year}/gws/merged_gw.csv",
            "teams": "https://raw.githubusercontent.com/vaastav/Fantasy-Premier-League/master/data/{season_year}/teams.csv",
            "fixtures": "https://raw.githubusercontent.com/vaastav/Fantasy-Premier-League/master/data/{season_year}/fixtures.csv",
            "players_raw": "https://raw.githubusercontent.com/vaastav/Fantasy-Premier-League/master/data/{season_year}/players_raw.csv"
        }

        for year in range(start_year, end_year):
            season_year = f"{year}-{str(year + 1)[-2:]}"
            for dataset_name, base_url in datasets.items():
                try:
                    csv_text, source_url = fetch_fpl_historical_data(base_url, season_year)
                    if csv_text and not csv_text.isspace():
                        gcs_path = f"raw/fpl_historical/{dataset_name}/{season_year.replace('-', '_')}/"
                        save_csv_to_gcs(bucket_name, csv_text, gcs_path, source_date, season_year, source_url)
                    else:
                        logging.warning(f"No data returned for {dataset_name} for season {season_year}. Skipping.")
                except Exception as e:
                    # Log error and continue with other datasets/seasons
                    logging.error(f"Error processing {dataset_name} for {season_year}: {e}")

        logging.info("Historical data ingestion complete")
        return {"status": "success"}

    except Exception as e:
        logging.error(f"Error during historical data ingestion: {e}")
        raise

if __name__ == "__main__":
    # This allows local execution without a functions framework server
    # For passing arguments, you would need to create a mock request object
    from unittest.mock import Mock
    mock_request = Mock()

    # Set custom years for test run
    mock_request.args = {
        'start_year': 2024,
        'end_year': 2025
    }
    
    ingest_fpl_historical(mock_request)