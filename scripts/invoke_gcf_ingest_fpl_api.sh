#!/bin/bash

curl -X GET https://ingest-fpl-api-1066298579404.australia-southeast1.run.app \
-H "Authorization: bearer $(gcloud auth print-identity-token)" \
-H "Content-Type: application/json"