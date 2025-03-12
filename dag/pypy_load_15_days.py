from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
import logging
import requests  # Ajout de requests

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
}

ENDPOINT_URL = "https://test-oscareo-service-749045337548.us-central1.run.app/load-pypi"

def call_endpoint(**kwargs):
    """
    Appelle l'endpoint Cloud Run avec requests et pousse la réponse dans XCom.
    """
    try:
        response = requests.get(ENDPOINT_URL, timeout=60)
        response.raise_for_status()  # Lève une exception si le statut n'est pas 200
        response_data = response.json()  # Suppose que la réponse est en JSON
        logging.info(f"Réponse reçue : {response_data}")
        # Pousse la réponse dans XCom pour la tâche suivante
        kwargs['ti'].xcom_push(key='endpoint_response', value={
            'status_code': response.status_code,
            'data': response_data
        })
    except requests.exceptions.RequestException as e:
        logging.error(f"Erreur lors de l'appel de l'endpoint : {str(e)}")
        raise

def check_response_status(**kwargs):
    """
    Vérifie que le statut de la réponse est 200.
    """
    response = kwargs['ti'].xcom_pull(task_ids='call_endpoint', key='endpoint_response')
    if not response or response.get('status_code') != 200:
        raise ValueError(f"Erreur : Code HTTP {response.get('status_code')} reçu au lieu de 200")
    logging.info("Réponse 200")

with DAG(
    'pypy_load_15_days',
    default_args=default_args,
    description='Appelle endpoint Cloud Run et vérifie le statut 200',
    schedule_interval='0 0 * * *',  # Exécute tous les jours à minuit
    start_date=days_ago(1),
    catchup=False,
) as dag:

    call_endpoint_task = PythonOperator(
        task_id='call_endpoint',
        python_callable=call_endpoint,
        provide_context=True,
    )

    validate_response_task = PythonOperator(
        task_id='validate_response',
        python_callable=check_response_status,
        provide_context=True,
    )

    call_endpoint_task >> validate_response_task