#!/bin/bash
gcloud dataproc clusters create etl-features-cluster \
    --region=australia-southeast1 \
    --master-machine-type=n1-standard-2 \
    --worker-machine-type=n1-standard-2 \
    --num-workers=2 \
    --worker-boot-disk-size=100GB \
    --master-boot-disk-size=100GB