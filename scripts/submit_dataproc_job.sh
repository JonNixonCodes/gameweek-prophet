#!/bin/bash
gcloud dataproc jobs submit pyspark src/dataproc/etl_features/main.py \
    --cluster=etl-features-cluster \
    --region=australia-southeast1 \
    --files=config/dataproc/etl_features/20250813.json \
    -- \
    --job-config=20250813.json