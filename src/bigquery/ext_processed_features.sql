CREATE OR REPLACE EXTERNAL TABLE `leverageai-sandbox.source.ext_processed_features`
OPTIONS (
  format = 'PARQUET',
  uris = ['gs://leverageai-sandbox-data/processed/features/20250410_035450/features.parquet/*.parquet']
);