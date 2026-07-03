from abc import ABC, abstractmethod
from app_config import BaseConfig
from pyspark.sql import SparkSession


class BaseJob(ABC):
    def __init__(self, job_name: str, environment: str) -> None:
        self.job_name = job_name
        self.environment = environment

        # Triggers our intelligent pathing resolution automatically
        self.config = BaseConfig(job_name=job_name, environment=environment)
        self.spark = self._init_spark()

    def _init_spark(self) -> SparkSession:
        spark_cfg = self.config.get("spark", {})
        builder = SparkSession.builder.appName(spark_cfg.get("app_name", self.job_name))
        for k, v in spark_cfg.get("config", {}).items():
            builder = builder.config(k, v)
        return builder.getOrCreate()

    @abstractmethod
    def run(self) -> None:
        pass