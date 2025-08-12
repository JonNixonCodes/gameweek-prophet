# Ingest FPL Historical Data Cloud Function

This document provides instructions on how to run the `ingest_fpl_historical` Google Cloud Function locally for testing and development.

## Local Execution

To run this function locally, follow these steps:

1.  **Create and Activate a Python Virtual Environment (Recommended):**

    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

2.  **Install Dependencies:**

    Install the required Python packages using pip:

    ```bash
    pip install -r requirements.txt
    ```

3.  **Configure Google Cloud Authentication:**

    Ensure your local environment is authenticated with Google Cloud, as the function interacts with Google Cloud Storage. You typically do this by running:

    ```bash
    gcloud auth application-default login
    ```

4.  **Run the Function Directly:**

    You can execute the `main.py` script directly. This will run the `ingest_fpl_historical` function with default parameters (ingesting data for the last few seasons).

    ```bash
    python3 main.py
    ```

    To pass custom `start_year` and `end_year` parameters, you can modify the `if __name__ == "__main__":` block within `main.py` to set `mock_request.args` accordingly. For example:

    ```python
    # Inside main.py, in the if __name__ == "__main__": block
    mock_request.args = {
        'start_year': 2020,
        'end_year': 2022
    }
    ```