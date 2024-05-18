from airflow.decorators import dag, task
from datetime import datetime
from airflow.providers.dbt.cloud.hooks.dbt import DbtCloudHook, DbtCloudJobRunStatus
from airflow.providers.dbt.cloud.operators.dbt import DbtCloudRunJobOperator
from airflow.providers.http.operators.http import SimpleHttpOperator
from airflow.providers.http.sensors.http import HttpSensor
from airflow.models import Variable
import json
from time import sleep

#===============
# dbt info
DBT_CLOUD_CONN_ID = "dbt-connection"
JOB_ID = "70403103935011"
#===============

#===============
# airbyte info
AIRBYTE_GOOGLE_CONNECTION_ID = Variable.get("AIRBYTE_GOOGLE_POSTGRES_CONNECTION_ID")
AIRBYTE_BIGQUERY_CONNECTION_ID = Variable.get("AIRBYTE_BIGQUERY_POSTGRES_CONNECTION_ID")
API_KEY = f'Bearer {Variable.get("AIRBYTE_API_TOKEN")}'
#===============


@dag(
        schedule="@daily",
        start_date=datetime(2024, 4, 19),
        catchup=False
)
def running_pipeline_dbt_airbyte():

    # sync airbyte bigquery
    start_airbyte_sync_bigquery = SimpleHttpOperator(
        task_id='start_airbyte_sync_bigquery',
        http_conn_id='airbyte',
        endpoint=f'/v1/jobs',
        method='POST',
        headers={"Content-Type": "application/json",
                 "User-Agent":"fake-useragent",
                 "Accept":"application/json",
                 "Authorization": API_KEY},
        data=json.dumps({"connectionId": AIRBYTE_BIGQUERY_CONNECTION_ID, "jobType":"sync"}),
        response_check=lambda response: response.json()['status'] == 'running' 
    )
    
    # sync airbyte google sheets
    start_airbyte_sync_gsheets = SimpleHttpOperator(
        task_id='start_airbyte_sync_gsheets',
        http_conn_id='airbyte',
        endpoint=f'/v1/jobs',
        method='POST',
        headers={"Content-Type": "application/json",
                 "User-Agent":"fake-useragent",
                 "Accept":"application/json",
                 "Authorization": API_KEY},
        data=json.dumps({"connectionId": AIRBYTE_GOOGLE_CONNECTION_ID, "jobType":"sync"}),
        response_check=lambda response: response.json()['status'] == 'running' 
    )

    @task
    def operador_http_sensor():
        sleep(300)
    
    # operator to run dbt
    run_dbt = DbtCloudRunJobOperator(
        task_id="run_dbt",
        dbt_cloud_conn_id=DBT_CLOUD_CONN_ID,
        job_id=JOB_ID,
        check_interval=60,
        timeout=360
    )

    t1 = operador_http_sensor()

    # running airbyte tasks in parallel, sleep for 5 min
    # and then running dbt

    [start_airbyte_sync_bigquery, start_airbyte_sync_gsheets] >> t1 >> run_dbt


running_pipeline_dbt_airbyte()