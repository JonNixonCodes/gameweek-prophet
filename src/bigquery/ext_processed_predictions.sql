CREATE OR REPLACE EXTERNAL TABLE `leverageai-sandbox.source.ext_processed_predictions`
OPTIONS (
  format = 'PARQUET',
  uris = ['gs://leverageai-sandbox-data/processed/predictions/20250406_163428/predictions.parquet']
);