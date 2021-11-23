import datetime

import airflow.utils.dates
from airflow import DAG
from airflow.operators.dummy import DummyOperator
from airflow.sensors.external_task import ExternalTaskSensor

dag1 = DAG(
    dag_id="figure_6_20_dag_1",
    start_date=airflow.utils.dates.days_ago(3),
    schedule_interval="0 16 * * *",
)
dag2 = DAG(
    dag_id="figure_6_20_dag_2",
    start_date=airflow.utils.dates.days_ago(3),
    schedule_interval="0 18 * * *",
)

DummyOperator(task_id="copy_to_raw", dag=dag1) >> DummyOperator(
    task_id="process_supermarket", dag=dag1
)

wait = ExternalTaskSensor(
    task_id="wait_for_process_supermarket",
    external_dag_id="figure_6_20_dag_1", # dag sur lequel on attend la tache
    external_task_id="process_supermarket", #task attendu du dag attendu tres utile si un dag a de multiple dependance
    execution_delta=datetime.timedelta(hours=6), #le temps d'attente pour qu'il y ai un chevauchement entre la tache cibler et l'external sensor
    dag=dag2,
)
report = DummyOperator(task_id="report", dag=dag2)
wait >> report
