from transformers.base import BaseTransformer
from pyspark.sql import DataFrame
from pyspark.sql.functions import udf
from pyspark.sql.types import StringType
import logging

logger = logging.getLogger(__name__)


# 1. Define the raw Python logic
def calculate_letter_grade(gpa: float) -> str:
    if gpa is None:
        return "N/A"
    if gpa >= 3.5:
        return "A"
    elif gpa >= 3.0:
        return "B"
    elif gpa >= 2.5:
        return "C"
    else:
        return "D"


# 2. Register it as a reusable PySpark UDF
# We specify StringType() because the output of the function is text data
letter_grade_udf = udf(calculate_letter_grade, StringType())


class GradeEnrichmentTransformer(BaseTransformer):
    """Applies a Python UDF to map numeric GPA scores to Letter Grades."""

    def __init__(self, input_col: str, output_col: str) -> None:
        self.input_col = input_col
        self.output_col = output_col

    def transform(self, df: DataFrame) -> DataFrame:
        logger.debug("Applying GradeEnrichment UDF on column: %s", self.input_col)

        # Apply the UDF wrapper to add a brand new column
        return df.withColumn(self.output_col, letter_grade_udf(df[self.input_col]))