# Secret Manager Configuration
# Migrated secrets from AWS Secrets Manager

locals {
  secrets = [
    "session-secret",
    "recaptcha-v2-secret-key",
    "apple-shared-secret",
    "google-service-account",
    "jwt-secret",
    "qr-encryption-key",
    "sendgrid-api-key",
  ]
}

# Create secrets in Secret Manager
resource "google_secret_manager_secret" "secrets" {
  for_each = toset(local.secrets)
  
  secret_id = each.key
  
  replication {
    auto {}  # Automatic replication to all regions
  }
}

# Grant Cloud Run service account access to secrets
resource "google_secret_manager_secret_iam_member" "secret_access" {
  for_each = toset(local.secrets)
  
  secret_id = google_secret_manager_secret.secrets[each.key].id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.app_service_account.email}"
}

# Note: Secret values must be added manually or via CLI
# Example:
# echo -n "your-secret-value" | gcloud secrets versions add session-secret --data-file=-

output "secrets_created" {
  value       = local.secrets
  description = "Secrets created in Secret Manager. Add values using gcloud CLI or Console."
}
