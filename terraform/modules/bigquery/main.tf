provider "google" {
  project = var.project_id
  region  = var.region
}

resource "google_bigquery_dataset" "pypi_dataset_resource" {
    dataset_id = var.pypi_dataset
    location = var.region
}

resource "google_bigquery_table" "pypi_table_download_15days_ressource" {
  dataset_id = google_bigquery_dataset.pypi_dataset_resource.dataset_id
  table_id   = var.pypi_table_download_15days
  project    = var.project_id
  
  schema = file("${path.module}/schema/schema_pypi_download_15days.json")  

  time_partitioning {
  type            = "DAY"
  field           = "timestamp"
  }

  deletion_protection = false
  description         = "Table contenant les téléchargements PyPI des 15 derniers jours"

  depends_on = [ google_bigquery_dataset.pypi_dataset_resource ]
}

resource "google_bigquery_table" "pypi_view_country_last_download_ressource" {
  dataset_id = google_bigquery_dataset.pypi_dataset_resource.dataset_id
  table_id   = var.pypi_view_country_last_download
  deletion_protection = false

  view {
    query = templatefile("${path.module}/views/country_last_download.sql", {
      project_id = var.project_id
      dataset_id = var.pypi_dataset
      table_id   = var.pypi_table_download_15days
    })
    use_legacy_sql = false
  }

  depends_on = [google_bigquery_dataset.pypi_dataset_resource, google_bigquery_table.pypi_table_download_15days_ressource ]
}

resource "google_bigquery_table" "pypi_view_all_download_details_ressource" {
  dataset_id = google_bigquery_dataset.pypi_dataset_resource.dataset_id
  table_id   = var.pypi_view_all_download_details
  deletion_protection = false

  view {
    query = templatefile("${path.module}/views/all_download_details.sql", {
      project_id = var.project_id
      dataset_id = var.pypi_dataset
      table_id   = var.pypi_table_download_15days
    })
    use_legacy_sql = false
  }

  depends_on = [google_bigquery_dataset.pypi_dataset_resource, google_bigquery_table.pypi_table_download_15days_ressource]
}