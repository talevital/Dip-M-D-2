import argparse
import os
import sys
import pandas as pd
from loguru import logger

from etl.extract.csv_extractor import CSVExtractor
from etl.transform.clean_data import DataCleaner
from etl.transform.normalize_data import DataNormalizer
from etl.transform.enrich_data import DataEnricher
from etl.load.load_postgres import PostgreSQLLoader
from utils.helpers import DataProfiler


def run_etl(input_csv: str, output_dir: str) -> int:
    logger.add(os.path.join(output_dir, "etl_upload.log"), rotation="1 day", retention="7 days")

    extractor = CSVExtractor()
    cleaner = DataCleaner()
    normalizer = DataNormalizer()
    enricher = DataEnricher()
    profiler = DataProfiler()

    logger.info(f"Reading CSV: {input_csv}")
    df = extractor.read_csv(input_csv)
    extractor.validate_csv(df)

    profile_initial = profiler.profile_dataframe(df)

    df = cleaner.clean_data(df)
    df = normalizer.normalize_data(df)
    df = enricher.enrich_data(df)

    os.makedirs(output_dir, exist_ok=True)
    out_csv = os.path.join(output_dir, "output.csv")
    df.to_csv(out_csv, index=False)

    profile_final = profiler.profile_dataframe(df)
    try:
        profiler.save_profile(profile_final, os.path.join(output_dir, "profile.json"))
    except Exception as e:
        logger.warning(f"Failed saving profile: {e}")

    db_url = os.getenv("DATABASE_URL")
    if db_url:
        try:
            loader = PostgreSQLLoader(db_url)
            if loader.test_connection():
                loader.load_data(df, table_name="uploads_etl", if_exists="append")
                loader.close_connection()
        except Exception as e:
            logger.warning(f"DB load skipped due to error: {e}")

    logger.info(f"ETL completed. Wrote: {out_csv}")
    return 0


def main():
    parser = argparse.ArgumentParser(description="Run ETL on an input CSV")
    parser.add_argument("--input", required=True, help="Path to input CSV")
    parser.add_argument("--output-dir", default="outputs", help="Directory to write outputs")
    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"Input file not found: {args.input}", file=sys.stderr)
        sys.exit(2)

    sys.exit(run_etl(args.input, args.output_dir))


if __name__ == "__main__":
    main()


