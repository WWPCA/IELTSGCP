# Cloud Functions Configuration

# Storage bucket for Cloud Functions source code
resource "google_storage_bucket" "functions_source" {
  name     = "${var.project_id}-cloud-functions-source"
  location = var.primary_region
  
  uniform_bucket_level_access = true
  
  lifecycle_rule {
    condition {
      age = 30
    }
    action {
      type = "Delete"
    }
  }
}

# Receipt Validation Cloud Function
resource "google_cloudfunctions2_function" "receipt_validation" {
  name        = "receipt-validation"
  location    = var.primary_region
  description = "Validate Apple App Store and Google Play receipts"
  
  build_config {
    runtime     = "python311"
    entry_point = "validate_receipt"
    
    source {
      storage_source {
        bucket = google_storage_bucket.functions_source.name
        object = "receipt_validation.zip"
      }
    }
  }
  
  service_config {
    max_instance_count = 10
    min_instance_count = 0
    available_memory   = "512Mi"
    timeout_seconds    = 60
    
    service_account_email = google_service_account.app_service_account.email
    
    environment_variables = {
      GOOGLE_CLOUD_PROJECT = var.project_id
      ANDROID_PACKAGE_NAME = "com.ieltsaiprep.app"
    }
    
    secret_environment_variables {
      key        = "APPLE_SHARED_SECRET"
      project_id = var.project_id
      secret     = "apple-shared-secret"
      version    = "latest"
    }
    
    secret_environment_variables {
      key        = "GOOGLE_SERVICE_ACCOUNT_JSON"
      project_id = var.project_id
      secret     = "google-service-account"
      version    = "latest"
    }
  }
}

# QR Code Handler Cloud Function
resource "google_cloudfunctions2_function" "qr_code_handler" {
  name        = "qr-code-handler"
  location    = var.primary_region
  description = "Generate and validate QR codes for mobile-to-web authentication"
  
  build_config {
    runtime     = "python311"
    entry_point = "handle_qr_code"
    
    source {
      storage_source {
        bucket = google_storage_bucket.functions_source.name
        object = "qr_code_handler.zip"
      }
    }
  }
  
  service_config {
    max_instance_count = 10
    min_instance_count = 0
    available_memory   = "256Mi"
    timeout_seconds    = 30
    
    service_account_email = google_service_account.app_service_account.email
    
    environment_variables = {
      GOOGLE_CLOUD_PROJECT = var.project_id
    }
  }
}

# Session Cleanup Cloud Function (called by Cloud Scheduler)
resource "google_cloudfunctions2_function" "session_cleanup" {
  name        = "cleanup-sessions"
  location    = var.primary_region
  description = "Clean up expired Firestore sessions"
  
  build_config {
    runtime     = "python311"
    entry_point = "cleanup_sessions"
    
    source {
      storage_source {
        bucket = google_storage_bucket.functions_source.name
        object = "session_cleanup.zip"
      }
    }
  }
  
  service_config {
    max_instance_count = 1
    min_instance_count = 0
    available_memory   = "256Mi"
    timeout_seconds    = 300
    
    service_account_email = google_service_account.app_service_account.email
    
    environment_variables = {
      GOOGLE_CLOUD_PROJECT = var.project_id
    }
  }
}

# Allow public access to HTTP functions
resource "google_cloud_run_service_iam_member" "receipt_validation_public" {
  service  = google_cloudfunctions2_function.receipt_validation.name
  location = google_cloudfunctions2_function.receipt_validation.location
  role     = "roles/run.invoker"
  member   = "allUsers"
}

resource "google_cloud_run_service_iam_member" "qr_code_handler_public" {
  service  = google_cloudfunctions2_function.qr_code_handler.name
  location = google_cloudfunctions2_function.qr_code_handler.location
  role     = "roles/run.invoker"
  member   = "allUsers"
}

# Outputs
output "receipt_validation_url" {
  value = google_cloudfunctions2_function.receipt_validation.service_config[0].uri
}

output "qr_code_handler_url" {
  value = google_cloudfunctions2_function.qr_code_handler.service_config[0].uri
}
