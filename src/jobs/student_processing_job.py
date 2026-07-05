import logging

from core.job import BaseJob
from transformers.cleanup import CastColumnTransformer, FilterTransformer
from transformers.custom_enrichment import GradeEnrichmentTransformer

logger = logging.getLogger(__name__)


class StudentProcessingJob(BaseJob):
    """ETL Job to clean student records by casting types and filtering by age."""

    def run(self) -> None:
        # 1. Fetch paths from config
        input_path = self.config.get("job", {}).get("input", {}).get("path")
        output_path = self.config.get("job", {}).get("output", {}).get("path")

        # Extract specific transformation rules from configuration
        tx_config = self.config.get("transformations", {})
        cast_mapping = tx_config.get("cast_types", {})
        filter_expr = tx_config.get("filter_condition", "age >= 0")

        # 2. Extract / Read
        logger.info("Reading raw student data from: %s", input_path)
        raw_df = self.spark.read.parquet(input_path)

        print("--- Raw Input Schema & Data ---")
        raw_df.printSchema()
        raw_df.show()

        # 3. Transform (Applying Cast and Filter Transformers sequentially)
        logger.info("Initializing transformation pipeline...")

        # We instantiate the transformers using the configuration dictionary data
        cast_transformer = CastColumnTransformer(cast_mapping)
        filter_transformer = FilterTransformer(filter_expr)

        # Instantiate our dynamic UDF Transformer (Read from 'gpa', write to new 'letter_grade')
        udf_transformer = GradeEnrichmentTransformer(input_col="gpa", output_col="letter_grade")

        # Execute pipeline
        df_casted = cast_transformer.transform(raw_df)
        df_filtered = filter_transformer.transform(df_casted)
        processed_df = udf_transformer.transform(df_filtered)

        # 4. Load / Write
        print("--- Processed Output Schema & Data ---")
        processed_df.printSchema()
        processed_df.show()

        logger.info("Writing clean student data to: %s", output_path)
        processed_df.write.mode("overwrite").parquet(output_path)