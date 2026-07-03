from __future__ import annotations

from abc import ABC, abstractmethod

from pyspark.sql import DataFrame

class BaseTransformer(ABC):
    """Abstract base class for all DataFrame transformers

    Each concrete transformer encapsulates a single, testable transformation step
    Chain multiple transformers in a job for complex pipelines.
    """

    @abstractmethod
    def transform(self, df:DataFrame) -> DataFrame:
        """Apply transformation to the input DataFrame

        :args
            df: Input DataFrame

        :returns
            Transformed DataFrame
        """

    def __call__(self, df: DataFrame) -> DataFrame:
        return self.transform(df)