from urllib import request

import airflow
from airflow import DAG
from airflow.operators.python import PythonOperator

dag = DAG(
    dag_id="stocksense",
    start_date=airflow.utils.dates.days_ago(1),
    schedule_interval="@hourly",
)


def _print_context(**context):
    """
    Acces aux dates par le contexte
    """
    start = context["execution_date"]
    end = context["next_execution_date"]
    print(f"Start: {start}, end: {end}")


print_context = PythonOperator(
    task_id="print_context", python_callable=_print_context, dag=dag
)
