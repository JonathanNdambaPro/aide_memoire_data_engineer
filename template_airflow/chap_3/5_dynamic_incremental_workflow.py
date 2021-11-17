import datetime as dt
from pathlib import Path
 
import pandas as pd
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
 
#Dag non fonctionnel api non existante continue indefiniment si end data non specifie
dag = DAG( 
    dag_id="04_time_delta", 
    schedule_interval= dt.timedelta(days=3) ,   #Tout les 3 jours
    start_date=dt.datetime(year=2019, month=1, day=1), 
    end_date=dt.datetime(year=2019 , month=1, day=5), #sinon specifier continue a l'infinie
)

#premiere option

optional_fetch_events = BashOperator(
    task_id="fetch_events",
    bash_command=(
         "mkdir -p /data && "
         "curl -o /data/events_{{execution_date.strftime('%Y-%m-%d')}}.json " #cree un fichier pour chaque jour empeche d'ecraser les fichiers des date precedentes pour creer un historique
         "http://localhost:5000/events?"
         "start_date={{execution_date.strftime('%Y-%m-%d')}}"  #Debut aggregat des donnes dynamic   
         "&end_date={{next_execution_date.strftime('%Y-%m-%d')}}" #Fin aggregat des donnes dynamic     
    ),
    dag=dag,
)

#Deuxieme option

fetch_events = BashOperator(
   task_id="fetch_events",
   bash_command=(
     "mkdir -p /data && "
     "curl -o /data/events_{{ds}}.json "  #cree un fichier pour chaque jour empeche d'ecraser les fichiers des date precedentes pour creer un historique 
      "http://localhost:5000/events?"
      "start_date={{ds}}&" #Debut aggregat des donnes dynamic  
      "end_date={{next_ds}}" #Fin aggregat des donnes dynamic        
   ),
   dag=dag,
)

def _calculate_stats(**context):                             
   """Calculates event statistics."""
   input_path = context["templates_dict"]["input_path"] #appel de variable externe  
   output_path = context["templates_dict"]["output_path"] #idem
 
   Path(output_path).parent.mkdir(exist_ok=True)
 
   events = pd.read_json(input_path)
   stats = events.groupby(["date", "user"]).size().reset_index()
   stats.to_csv(output_path, index=False)
 
 
calculate_stats = PythonOperator(
   task_id="calculate_stats",
   python_callable=_calculate_stats,
   templates_dict={
       "input_path": "/data/events/events_{{ds}}.json", # variable path d'entree          
       "output_path": "/data/stats/events_{{ds}}.csv", # variable path de sortie 
   },
   dag=dag,
)
 
fetch_events >> calculate_stats 