terraform {
    required_version = ">= 1.0"
    backend "local" {}
    required_providers {
      google = {
        source = "hashicorp/google"
      }
    }

}

provider "google" {
  project = var.project
  region = var.region
}


resource "google_storage_bucket" "data-lake-bucket" {
    name = "${local.data_lake_bucket}_${var.project}"
    location = var.region

    # optional, but recommended settings:
    storage_class = var.storage_class
    uniform_bucket_level_access = true

    versioning {
        enabled = true
    }

    lifecycle_rule {
        action {
            type = "Delete"
        }

    condition {
        age = 30 //data
    }
}

    
        force_destroy = true
}

# DWH
resource "google_bigquery_dataset" "dataset" {
    dataset_id = var.BQ_DATASET 
    project = var.project
    location = var.region
}

resource "google_dataproc_cluster" "datazoomidcluster" {
    name = "datazoomidcluster"
    region = "europe-west4"
    
    cluster_config {

        master_config {
            num_instances = 1
            machine_type = "n2-standard-2"
            disk_config {
                boot_disk_type = "pd-standard"
                boot_disk_size_gb = 200
            }
        }
    
    software_config {
        image_version = "2.0-debian10"
        override_properties = {
            "dataproc:dataproc.allow.zero.workers" = "true"
        }
    }
    }
    }