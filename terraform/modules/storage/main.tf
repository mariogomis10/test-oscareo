resource "google_storage_bucket" "bucket_pypi_ressource" {
  name          = var.bucket_pypi_download_daily
  location      = var.region
  project       = var.project_id
  versioning {
    enabled = true
  }
}
