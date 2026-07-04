"""Reusable, composable DataFrame transformers"""

from __future__ import annotations

from pyspark.sql import DataFrame, functions as F
from pyspark.sql.types import DataType

from src.utils.logger import get_logger
from transformers.base import BaseTransformer

logger = get_logger(__name__)

class DropDuplicatesTransformer(BaseTransformer):
    """Remove duplicate rows based on a set of key column"""

    def __init__(self, subset: list[str] | None = None) -> None:
        self.subset = subset

    def transform(self, df:DataFrame) -> DataFrame:
        logger.debug("Dropping duplicates on columns: %s", self.subset)
        return df.dropDuplicates(self.subset) if self.subset else df.dropDuplicates()

class DropNullsTransformer(BaseTransformer):
    """Drop rows containing null values in specified column"""

    def __init__(self, subset:list[str] | None = None) -> None:
        self.subset = subset

    def transform(self, df:DataFrame) -> DataFrame:
        logger.debug("Dropping nulls on columns: %s", self.subset)
        return df.dropna(subset=self.subset)


class RenameColumnsTransformer(BaseTransformer):
    """Rename specified columns in a DataFrame using a mapping dictionary"""

    def __init__(self, mapping: dict[str, str]) -> None:
        self.mapping = mapping

    def transform(self, df: DataFrame) -> DataFrame:
        logger.debug("Renaming columns with mapping: %s", self.mapping)
        for old_name, new_name in self.mapping.items():
            df = df.withColumnRenamed(old_name, new_name)
        return df


class CastColumnTransformer(BaseTransformer):
    """Cast specific columns to given data types"""

    def __init__(self, casts: dict[str, DataType]) -> None:
        self.casts = casts

    def transform(self, df: DataFrame) -> DataFrame:
        logger.debug("Casting columns with mapping: %s", self.casts)
        for column, dtype in self.casts.items():
            df = df.withColumn(column, F.col(column).cast(dtype))
        return df


class FilterTransformer(BaseTransformer):
    """Filter rows based on a given SQL expression string or Column condition"""

    def __init__(self, condition: str) -> None:
        self.condition = condition

    def transform(self, df: DataFrame) -> DataFrame:
        logger.debug("Filtering DataFrame using condition: %s", self.condition)
        return df.filter(self.condition)

class AddAuditColumnTransformer(BaseTransformer):
    """Append standard audit columns (processed_at, source_system"""

    def __init__(self, source_system: str) -> None:
        self.source_system = source_system

    def transform(self, df: DataFrame) -> DataFrame:
        return df.withColumn("processed_at", F.current_timestamp()).withColumn(
            "source_system", F.lit(self.source_system)
        )

def pipeline(*transformers: BaseTransformer) -> BaseTransformer:
    """Compose multiple transformers into a single callable.

    :args
        *transformers: Ordered sequence of BaseTransformer instances

    :returns
        A BaseTransformer that applies all steps in order

    Example:
        pipe = pipeline(
            DropDuplicatesTransformer(["id"]),
            DropNullsTransformer(["id", "amount"]),
            AddAuditColumnsTransformer("payments"),
            )
            result_df = pipe(input_df)
    """

    class _Pipeline(BaseTransformer):
        def transform(self, df:DataFrame) -> DataFrame:
            for t in transformers:
                df = t(df)
            return df

    return _Pipeline()


