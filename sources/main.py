from fastapi import FastAPI, HTTPException
from google.cloud import bigquery
from google.cloud import storage  
import json
from datetime import datetime  

app = FastAPI(
    title="Pypi Data BigQuery Load API",
    description="API pour charger les données PyPI dans BigQuery",
    version="1.0.0"
)

# Initialisation des clients BigQuery et GCS
client = bigquery.Client()
storage_client = storage.Client()

# Chargement de la configuration
def load_config():
    with open('config.json', 'r') as config_file:
        return json.load(config_file)

# Chargement des requête SQL
def load_query(file_name):
    with open(file_name, 'r') as file:
        return file.read()

@app.get("/load-pypi", 
         summary="Charge les données PyPI des 15 derniers jours",
         response_description="Statut de l'exécution de la requête")
async def load_pypi_data():
    """
    Exécute la requête SQL pour charger les données PyPI des 15 derniers jours dans BigQuery.
    Retourne un message de succès ou une erreur.
    """
    try:
        # Chargement de la config et de la requête
        config = load_config()
        query = load_query('load_pypi_last_15_days.sql')
        
        destination_table = config["destination_table"]

        # Configuration du job BigQuery
        job_config = bigquery.QueryJobConfig(
            destination=destination_table,
            write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE
        )

        # Exécution de la requête
        query_job = client.query(query, job_config=job_config)
        query_job.result()  

        return {
            "status": "success",
            "message": f"Lignes insérées avec succès dans {destination_table}",
            "job_id": query_job.job_id
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'exécution : {str(e)}")

@app.get("/load-pypi-current-day",
         summary="Charge les données PyPI du jour actuel et exporte en JSON dans GCS",
         response_description="Statut de l'exécution et exportation")
async def load_pypi_current_day():
    """
    Exécute la requête SQL pour les données PyPI du jour actuel,
    génère des fichiers JSON nommés AAAAMMDD_part*.json et les dépose dans un bucket GCS.
    """
    try:
        config = load_config()
        query = load_query('load_pypi_current_day.sql')

        current_date = datetime.now().strftime("%Y%m%d")
        # Changement en .json avec * pour generer plusieur fichiers si besion
        json_filename = f"{current_date}_part*.json"  
        bucket_name = config["bucket_name"]

        job_config = bigquery.QueryJobConfig()
        query_job = client.query(query, job_config=job_config)
        query_job.result()

        bucket = storage_client.bucket(bucket_name)
        destination_uri = f"gs://{bucket_name}/{json_filename}"  
        
        extract_job_config = bigquery.ExtractJobConfig(
            # Export en JSONL
            destination_format=bigquery.DestinationFormat.NEWLINE_DELIMITED_JSON,  
            compression=None 
        )
        
        extract_job = client.extract_table(
            query_job.destination,
            destination_uri,
            job_config=extract_job_config
        )
        extract_job.result()

        return {
            "status": "success",
            "message": f"Données du jour exportées dans {destination_uri} (potentiellement plusieurs fichiers JSON)",
            "job_id": extract_job.job_id
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'exécution : {str(e)}")


# Point d'entrée pour Cloud Run
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)