# GCP Infrastructure for IELTS GenAI Prep
# Multi-Region Deployment: us-central1, europe-west1, asia-southeast1

terraform {
  required_version = ">= 1.0"
  
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
  
  backend "gcs" {
    bucket = "ielts-genai-prep-terraform-state"
    prefix = "terraform/state"
  }
}

# Variables
variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "primary_region" {
  description = "Primary region"
  type        = string
  default     = "us-central1"
}

variable "secondary_regions" {
  description = "Secondary regions"
  type        = list(string)
  default     = ["europe-west1", "asia-southeast1"]
}

variable "domain_name" {
  description = "Custom domain"
  type        = string
  default     = "www.ieltsaiprep.com"
}

# Provider
provider "google" {
  project = var.project_id
  region  = var.primary_region
}

# Enable required APIs
resource "google_project_service" "required_apis" {
  for_each = toset([
    "run.googleapis.com",
    "cloudfunctions.googleapis.com",
    "firestore.googleapis.com",
    "secretmanager.googleapis.com",
    "cloudbuild.googleapis.com",
    "artifactregistry.googleapis.com",
    "dns.googleapis.com",
    "cloudscheduler.googleapis.com",
    "aiplatform.googleapis.com",
    "language.googleapis.com",
  ])
  
  service            = each.key
  disable_on_destroy = false
}

# Service Account for Cloud Run
resource "google_service_account" "app_service_account" {
  account_id   = "ielts-app-sa"
  display_name = "IELTS GenAI Prep Application Service Account"
}

# IAM roles for service account
resource "google_project_iam_member" "app_roles" {
  for_each = toset([
    "roles/datastore.user",           # Firestore access
    "roles/secretmanager.secretAccessor", # Secrets access
    "roles/aiplatform.user",          # Vertex AI / Gemini access
    "roles/cloudfunctions.invoker",   # Call Cloud Functions
    "roles/logging.logWriter",        # Write logs
  ])
  
  project = var.project_id
  role    = each.key
  member  = "serviceAccount:${google_service_account.app_service_account.email}"
}

# Artifact Registry for container images
resource "google_artifact_registry_repository" "app_repo" {
  location      = var.primary_region
  repository_id = "ielts-genai-prep"
  description   = "Container images for IELTS GenAI Prep"
  format        = "DOCKER"
}

# Outputs
output "service_account_email" {
  value = google_service_account.app_service_account.email
}

output "artifact_registry_repo" {
  value = google_artifact_registry_repository.app_repo.name
}
