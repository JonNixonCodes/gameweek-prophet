#!/bin/bash

gcloud functions deploy ingest_fpl_api \
  --gen2 \
  --region australia-southeast1 \
  --runtime python310 \
  --source src/cloud_functions/ingest_fpl_api \
  --entry-point ingest_fpl_api \
  --set-env-vars BUCKET_NAME=leverageai-sandbox-data \
  --trigger-http \
  --no-allow-unauthenticated \
  --timeout 1800s \
  --memory 512MB
