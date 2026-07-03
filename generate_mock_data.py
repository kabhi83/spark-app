import os
import sys
from pyspark.sql import SparkSession


def create_mock_data():
    spark = SparkSession.builder.appName("MockDataGen").master("local[*]").getOrCreate()

    # Raw mock student data (Notice that age and gpa are purposefully wrapped as strings)
    mock_students = [
        ("Alice", "20", "3.8", "Computer Science"),
        ("Bob", "17", "3.2", "Mathematics"),  # Will be filtered out (Under 18)
        ("Charlie", "22", "2.9", "History"),
        ("Daisy", "16", "3.9", "Physics"),  # Will be filtered out (Under 18)
        ("Ethan", "19", "3.5", "Engineering")
    ]

    columns = ["name", "age", "gpa", "major"]
    df = spark.createDataFrame(mock_students, schema=columns)

    # Generate local path directory blocks
    os.makedirs("data/input", exist_ok=True)
    df.write.mode("overwrite").parquet("data/input/students.parquet")
    print("Successfully created mock dataset at data/input/students.parquet!")
    spark.stop()


if __name__ == "__main__":
    create_mock_data()