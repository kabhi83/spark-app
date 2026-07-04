from transformers.base import BaseTransformer
from pyspark.sql import DataFrame
from pyspark.sql.functions import pandas_udf
from pyspark.sql.types import StringType
import pandas as pd
import numpy as np


# 1. Define the Vectorized Python Function using Pandas
# Input is a Pandas Series of GPAs, Output is a Pandas Series of Strings
@pandas_udf(StringType())
def calculate_letter_grade_vectorized(gpa_series: pd.Series) -> pd.Series:
    # Instead of row-by-row if/else blocks, we use highly optimized NumPy vectorization
    conditions = [
        gpa_series.isna(),
        gpa_series >= 3.5,
        gpa_series >= 3.0,
        gpa_series >= 2.5
    ]
    choices = ["N/A", "A", "B", "C"]

    # default value handles anything less than 2.5 ("D")
    return pd.Series(np.select(conditions, choices, default="D"))


class VectorizedGradeEnrichmentTransformer(BaseTransformer):
    """Applies a Vectorized Pandas UDF via Apache Arrow for high throughput."""

    def __init__(self, input_col: str, output_col: str) -> None:
        self.input_col = input_col
        self.output_col = output_col

    def transform(self, df: DataFrame) -> DataFrame:
        # The syntax for applying it to the DataFrame remains identical
        return df.withColumn(self.output_col, calculate_letter_grade_vectorized(df[self.input_col]))