#!/bin/bash

# Replace with your actual Cloud Run service URL for ingest_fpl_historical
SERVICE_URL="https://ingest-fpl-historical-hvhy4lzhlq-ts.a.run.app"

# Optional: Set start and end years for ingestion
# Default values will be used if not provided
START_YEAR="2022" # Example: Start of 2022-23 season
END_YEAR="2025"   # Example: End of 2024-25 season

# Construct the URL with query parameters
URL="${SERVICE_URL}?start_year=${START_YEAR}&end_year=${END_YEAR}"

# Invoke the Cloud Run service
curl -X GET "${URL}" \
-H "Authorization: bearer $(gcloud auth print-identity-token)" \
-H "Content-Type: application/json"