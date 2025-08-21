CREATE OR REPLACE EXTERNAL TABLE
  `leverageai-sandbox.source.processed_features_ext`
WITH PARTITION COLUMNS OPTIONS ( format = 'PARQUET',
    uris = ['gs://leverageai-sandbox-data/processed/features/*.parquet'],
    hive_partition_uri_prefix = 'gs://leverageai-sandbox-data/processed/features/',
    require_hive_partition_filter = TRUE);