from airflow.decorators import dag, task
from datetime import datetime
from airflow.providers.http.operators.http import SimpleHttpOperator
from airflow.providers.http.sensors.http import HttpSensor
from airflow.models import Variable
import json
from datetime import datetime

AIRBYTE_BIGQUERY_CONNECTION_ID = Variable.get("AIRBYTE_BIGQUERY_POSTGRES_CONNECTION_ID")
AIRBYTE_GOOGLE_CONNECTION_ID = Variable.get("AIRBYTE_GOOGLE_POSTGRES_CONNECTION_ID")
API_KEY = f'Bearer {Variable.get("AIRBYTE_API_TOKEN")}'

@dag(
        schedule="@daily",
        start_date=datetime(2024, 4, 17),
        catchup=False
)
def running_airbyte():