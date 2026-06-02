"""
Airflow DAG for deal data ingestion pipeline
"""
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.postgres_operator import PostgresOperator

default_args = {
    "owner": "deal-analysis",
    "depends_on_past": False,
    "start_date": datetime(2024, 1, 1),
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 3,
    "retry_delay": timedelta(minutes=5),
}


def run_ingestion(**context):
    """Run the data ingestion pipeline"""
    from services.pipelines import DataIngestionPipeline

    pipeline = DataIngestionPipeline()

    def mock_source():
        # Mock data source - replace with actual data fetch
        return [
            {"name": "Deal 1", "value": 1000000, "type": "acquisition"},
            {"name": "Deal 2", "value": 2000000, "type": "merger"},
        ]

    def mock_transform(record):
        # Mock transformation
        return {
            "name": record["name"],
            "deal_value": record["value"],
            "deal_type": record["type"],
        }

    result = pipeline.execute(
        source_handler=mock_source,
        transformer=mock_transform,
    )
    return result


def run_spatial_processing(**context):
    """Run spatial data processing"""
    from services.pipelines import SpatialDataPipeline

    pipeline = SpatialDataPipeline()
    result = pipeline.execute(deal_ids=[])
    return result


def run_validation(**context):
    """Run data quality validation"""
    from services.pipelines import ValidationPipeline

    pipeline = ValidationPipeline()
    result = pipeline.execute(entity_type="Deal")
    return result


with DAG(
    "deal_data_pipeline",
    default_args=default_args,
    description="Daily deal data ingestion and processing",
    schedule_interval="0 2 * * *",  # Daily at 2 AM
    catchup=False,
    tags=["deals", "ingestion", "analytics"],
) as dag:

    start = PostgresOperator(
        task_id="start_pipeline",
        postgres_conn_id="postgres_default",
        sql="SELECT 1;",
    )

    ingestion = PythonOperator(
        task_id="run_data_ingestion",
        python_callable=run_ingestion,
    )

    spatial = PythonOperator(
        task_id="run_spatial_processing",
        python_callable=run_spatial_processing,
    )

    validation = PythonOperator(
        task_id="run_validation",
        python_callable=run_validation,
    )

    end = PostgresOperator(
        task_id="end_pipeline",
        postgres_conn_id="postgres_default",
        sql="SELECT 1;",
    )

    start >> ingestion >> spatial >> validation >> end