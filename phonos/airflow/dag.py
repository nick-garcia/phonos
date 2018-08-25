from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'me',
    'depends_on_past': False,
    'start_date': datetime(2018, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5)
}

def test():
    print("Test run!")

with DAG('phonos_importer', default_args=default_args, schedule_interval="0 * * * *") as dag:

    p = PythonOperator(python_callable=test, task_id='phonos_test')

p