from airflow.decorators import dag
from datetime import datetime
from airflow.providers.http.operators.http import SimpleHttpOperator
from airflow.providers.http.sensors.http import HttpSensor
from airflow.models import Variable
import json
from datetime import datetime

AIRBYTE_GOOGLE_CONNECTION_ID = Variable.get("AIRBYTE_GOOGLE_POSTGRES_CONNECTION_ID")
API_KEY = f'Bearer {Variable.get("AIRBYTE_API_TOKEN")}'

@dag(
        schedule="@daily",
        start_date=datetime(2024, 4, 17),
        catchup=False
)
def running_airbyte_googlesheets():
    start_airbyte_sync = SimpleHttpOperator(
        task_id='start_airbyte_sync',
        http_conn_id='aitbyte',
        endpoint=f'/v1/jobs',
        method='POST',
        headers={"Content-Type": "application/json",
                 "User-Agent":"fake-useragent",
                 "Accept":"application/json",
                 "Authorization": API_KEY},
        data=json.dumps({"connectionId": AIRBYTE_GOOGLE_CONNECTION_ID, "jobType":"sync"}),
        response_check=lambda response: response.json()['status'] == 'running' 
    )

    start_airbyte_sync

running_airbyte_googlesheets()