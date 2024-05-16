from airflow.decorators import dag, task
from datetime import datetime

@dag(
        dag_id="my_sweet_dag",
        description="dag used in pipeline",
        schedule="0 20 * * *",
        start_date=datetime(2024,4,16),
        catchup=False
)
def pipeline():

    @task
    def first_task():
        print("1")

    @task
    def second_task():
        print("2")

    @task
    def third_task():
        print("3")


    t1 = first_task()
    t2 = second_task()
    t3 = third_task()

    t1 >> t2 >> t3

pipeline()




