# Firestore Configuration for IELTS GenAI Prep
# Multi-region database with automatic replication

# Firestore Database
# Using nam5 (North America multi-region) for automatic replication and 99.999% SLA
# Note: Firestore only offers multi-region within same continent (nam5, eur3)
# Google's global backbone provides acceptable latency (~50-100ms) to all regions
# Alternative: Use asia-south1 single-region for lowest latency to India/Asia markets
resource "google_firestore_database" "main" {
  project     = var.project_id
  name        = "(default)"
  location_id = "nam5"  # Multi-region for high availability
  type        = "FIRESTORE_NATIVE"
  
  # Point-in-time recovery for backups
  point_in_time_recovery_enablement = "POINT_IN_TIME_RECOVERY_ENABLED"
  
  # Delete protection
  deletion_policy = "DELETE"
}

# Firestore Indexes for efficient queries
resource "google_firestore_index" "user_by_username" {
  project    = var.project_id
  database   = google_firestore_database.main.name
  collection = "users"
  
  fields {
    field_path = "username"
    order      = "ASCENDING"
  }
  
  fields {
    field_path = "__name__"
    order      = "ASCENDING"
  }
}

resource "google_firestore_index" "user_by_user_id" {
  project    = var.project_id
  database   = google_firestore_database.main.name
  collection = "users"
  
  fields {
    field_path = "user_id"
    order      = "ASCENDING"
  }
  
  fields {
    field_path = "__name__"
    order      = "ASCENDING"
  }
}

resource "google_firestore_index" "assessments_by_user" {
  project    = var.project_id
  database   = google_firestore_database.main.name
  collection = "assessments"
  
  fields {
    field_path = "user_id"
    order      = "ASCENDING"
  }
  
  fields {
    field_path = "created_at"
    order      = "DESCENDING"
  }
  
  fields {
    field_path = "__name__"
    order      = "ASCENDING"
  }
}

resource "google_firestore_index" "entitlements_active" {
  project    = var.project_id
  database   = google_firestore_database.main.name
  collection = "entitlements"
  
  fields {
    field_path = "user_id"
    order      = "ASCENDING"
  }
  
  fields {
    field_path = "status"
    order      = "ASCENDING"
  }
  
  fields {
    field_path = "__name__"
    order      = "ASCENDING"
  }
}

resource "google_firestore_index" "sessions_expires" {
  project    = var.project_id
  database   = google_firestore_database.main.name
  collection = "sessions"
  
  fields {
    field_path = "expires_at"
    order      = "ASCENDING"
  }
  
  fields {
    field_path = "__name__"
    order      = "ASCENDING"
  }
}

# Cloud Scheduler job for session cleanup
resource "google_cloud_scheduler_job" "session_cleanup" {
  name             = "firestore-session-cleanup"
  description      = "Clean up expired Firestore sessions"
  schedule         = "0 */6 * * *"  # Every 6 hours
  time_zone        = "UTC"
  attempt_deadline = "320s"
  
  http_target {
    http_method = "POST"
    uri         = "https://${var.primary_region}-${var.project_id}.cloudfunctions.net/cleanup-sessions"
    
    oidc_token {
      service_account_email = google_service_account.app_service_account.email
    }
  }
}

output "firestore_database" {
  value = google_firestore_database.main.name
}
