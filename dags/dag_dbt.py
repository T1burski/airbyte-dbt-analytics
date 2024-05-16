from airflow.decorators import dag, task
from datetime import datetime
from airflow.providers.dbt.cloud.hooks.dbt import DbtCloudHook, DbtCloudJobRunStatus
from airflow.providers.dbt.cloud.operators.dbt import DbtCloudRunJobOperator

DBT_CLOUD_CONN_ID = "dbt-connection"
JOB_ID = "70403103935011"

@dag(
        schedule="@daily",
        start_date=datetime(2024, 4, 17),
        catchup=False
)
def running_dbt_cloud():

    # operator to run dbt
    run_dbt = DbtCloudRunJobOperator(
        task_id="run_dbt",
        dbt_cloud_conn_id=DBT_CLOUD_CONN_ID,
        job_id=JOB_ID,
        check_intervals=60,
        timeout=360
    )

    run_dbt

running_dbt_cloud()


