from __future__ import annotations

import os
from typing import Optional

from pyspark.sql import SparkSession

def get_spark_session(
        app_name: str,
        config: Optional[dict] = None,
) -> SparkSession:
    """
    Build or retrieve the active SparkSession
    Args:
        :param app_name: Logical name for the Spark Application.
        :param config: Optional dict of additional Spark conf key-value pairs
    :return:
        Configured SparkSession
    """

    env = os.getenv("APP_ENV", "local")
    builder = SparkSession.builder.appName(app_name)

    # Adaptive query execution - on by default in Spark 3.x
    builder = builder.config("spark.sql.adaptive.enabled", "true")

    # Core Spark SQL & Optimizer Defaults
    builder = builder.config("spark.sql.parquet.compression.codec", "snappy")
    builder = builder.config("spark.sql.parquet.filterPushdown", "true")
    builder = builder.config("spark.sql.parquet.dictionary.encode", "false")
    builder = builder.config("spark.sql.parquet.mergeSchema", "false")

    # Vectorized Reader (Performance)
    builder = builder.config("spark.sql.parquet.enableVectorizedReader", "true")
    builder = builder.config("spark.sql.parquet.vectorizedReader.batchSize", "4096")

    # Timestamp & Datetime Compatibility
    builder = builder.config("spark.sql.parquet.datetimeRebaseModeInRead", "EXCEPTION")
    builder = builder.config("spark.sql.parquet.datetimeRebaseModeInWrite", "EXCEPTION")
    builder = builder.config("spark.sql.parquet.int96RebaseModeInRead", "EXCEPTION")
    builder = builder.config("spark.sql.parquet.int96RebaseModeInWrite", "EXCEPTION")
    builder = builder.config("spark.sql.parquet.int96AsTimestamp", "true")
    builder = builder.config("spark.sql.parquet.outputTimestampType", "INT96")

    # Write & Metadata Specs
    builder = builder.config("spark.sql.parquet.writeLegacyFormat", "false")
    builder = builder.config("spark.sql.parquet.recordLevelFilter.enabled", "false")

    # Infrastructure & Resource Configs
    builder = builder.config("spark.master", os.getenv("SPARK_MASTER", "local[*]"))
    builder = builder.config("spark.driver.memory", os.getenv("SPARK_DRIVER_MEMORY", "1g"))
    builder = builder.config("spark.executor.memory", os.getenv("SPARK_EXECUTOR_MEMORY", "1g"))

    # Performance & Tuning Configs
    builder = builder.config("spark.sql.shuffle.partitions", os.getenv("SPARK_SQL_SHUFFLE_PARTITIONS", "4"))
    builder = builder.config("spark.default.parallelism", os.getenv("SPARK_DEFAULT_PARALLELISM", "4"))
    builder = builder.config("spark.dynamicAllocation.enabled", os.getenv("SPARK_DYNAMIC_ALLOCATION", "false"))

    if config:
        for key, value in config.items():
            builder = builder.config(key, value)
    # Finalize the session
    return builder.getOrCreate()

def stop_spark_session(spark: SparkSession) -> None:
    """Gracefully stop SparkSession"""
    spark.stop()