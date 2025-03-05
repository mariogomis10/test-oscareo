# Test-Oscareo

Ce projet contient une API FastAPI pour charger des données PyPI dans BigQuery et les exporter vers Google Cloud Storage, 
ainsi qu'un DAG Airflow pour automatiser le processus via Google Cloud Composer.

## Prérequis

- Un projet GCP
- Les outils CLI GCP installés
- Accès à Cloud Build, Artifact Registry, Cloud Run, et Composer
- Un dataset Bigquery et un bucket GCS pour stocker les données exportées.


### Compte de service

Créez un compte de service Google Cloud avec les droits IAM nécessaires pour interagir avec BigQuery, GCS, Cloud Run, et Composer. Voici les rôles recommandés :
- `roles/bigquery.admin` : Pour exécuter des requêtes et exporter des données dans BigQuery.
- `roles/storage.admin` : Pour lire/écrire dans GCS.
- `roles/run.admin` : Pour déployer sur Cloud Run.
- `roles/composer.admin` : Pour gérer l'environnement Composer.

### Build de l'image avec Cloud Build
`gcloud builds submit --tag gcr.io/gcp-project/test-oscareo-v1`

### Déploiement de l'image sur Cloud Run
`gcloud run deploy test-oscareo-service \`
  `--image gcr.io/gcp-project/test-oscareo-v1 \ `
  `--platform managed \`
  `--region europe-west1 \`
  `--allow-unauthenticated \`
  `--memory 512Mi`

### Création d’une instance Composer et deposer 

### L'infrastructure pourra être realiser avec terraform 
