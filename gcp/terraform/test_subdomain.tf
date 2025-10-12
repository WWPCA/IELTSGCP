# Test Subdomain Configuration for test.ieltsaiprep.com
# Allows preview deployment before production

# Cloud Run service for test environment
resource "google_cloud_run_v2_service" "test_app" {
  name     = "ielts-genai-prep-test"
  location = var.primary_region
  
  template {
    service_account = google_service_account.app_service_account.email
    
    scaling {
      min_instance_count = 0  # Test can scale to zero to save costs
      max_instance_count = 3
    }
    
    containers {
      image = "${var.primary_region}-docker.pkg.dev/${var.project_id}/ielts-genai-prep/app:test"
      
      ports {
        container_port = 5000
      }
      
      resources {
        limits = {
          cpu    = "1"
          memory = "512Mi"
        }
        cpu_idle = true
      }
      
      # Environment variables
      env {
        name  = "GOOGLE_CLOUD_PROJECT"
        value = var.project_id
      }
      
      env {
        name  = "GOOGLE_CLOUD_REGION"
        value = var.primary_region
      }
      
      env {
        name  = "ENVIRONMENT"
        value = "test"
      }
      
      # Firestore will use "test_" prefix for all collections
      # This isolates test data from production data
      
      # Secrets from Secret Manager (same as production)
      dynamic "env" {
        for_each = toset([
          "SESSION_SECRET",
          "RECAPTCHA_V2_SECRET_KEY",
          "APPLE_SHARED_SECRET",
          "GOOGLE_SERVICE_ACCOUNT_JSON",
          "JWT_SECRET",
          "QR_ENCRYPTION_KEY",
          "SENDGRID_API_KEY"
        ])
        
        content {
          name = env.value
          value_source {
            secret_key_ref {
              secret  = lower(replace(env.value, "_", "-"))
              version = "latest"
            }
          }
        }
      }
    }
    
    timeout = "3600s"
  }
  
  traffic {
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
    percent = 100
  }
  
  depends_on = [google_project_service.required_apis]
}

# Allow unauthenticated access to test
resource "google_cloud_run_service_iam_member" "test_public_access" {
  service  = google_cloud_run_v2_service.test_app.name
  location = var.primary_region
  role     = "roles/run.invoker"
  member   = "allUsers"
}

# DNS record for test subdomain
resource "google_dns_record_set" "test_subdomain" {
  managed_zone = google_dns_managed_zone.ieltsaiprep.name
  name         = "test.ieltsaiprep.com."
  type         = "A"
  ttl          = 300
  
  rrdatas = [google_compute_global_address.test_ip.address]
}

# Separate IP for test environment
resource "google_compute_global_address" "test_ip" {
  name = "ielts-genai-prep-test-ip"
}

# Backend service for test
resource "google_compute_backend_service" "test" {
  name = "ielts-genai-prep-test-backend"
  
  protocol    = "HTTP"
  port_name   = "http"
  timeout_sec = 3600
  
  load_balancing_scheme = "EXTERNAL_MANAGED"
  
  backend {
    group           = google_compute_region_network_endpoint_group.test_neg.id
    balancing_mode  = "UTILIZATION"
    capacity_scaler = 1.0
  }
}

# NEG for test Cloud Run
resource "google_compute_region_network_endpoint_group" "test_neg" {
  name                  = "ielts-genai-prep-test-neg"
  network_endpoint_type = "SERVERLESS"
  region                = var.primary_region
  
  cloud_run {
    service = google_cloud_run_v2_service.test_app.name
  }
}

# URL map for test
resource "google_compute_url_map" "test" {
  name            = "ielts-genai-prep-test-url-map"
  default_service = google_compute_backend_service.test.id
}

# SSL certificate for test subdomain
resource "google_compute_managed_ssl_certificate" "test" {
  name = "ielts-genai-prep-test-ssl"
  
  managed {
    domains = ["test.ieltsaiprep.com"]
  }
}

# HTTPS proxy for test
resource "google_compute_target_https_proxy" "test" {
  name             = "ielts-genai-prep-test-https-proxy"
  url_map          = google_compute_url_map.test.id
  ssl_certificates = [google_compute_managed_ssl_certificate.test.id]
}

# Forwarding rule for test
resource "google_compute_global_forwarding_rule" "test_https" {
  name                  = "ielts-genai-prep-test-https"
  ip_protocol           = "TCP"
  load_balancing_scheme = "EXTERNAL_MANAGED"
  port_range            = "443"
  target                = google_compute_target_https_proxy.test.id
  ip_address            = google_compute_global_address.test_ip.id
}

# HTTP redirect for test
resource "google_compute_url_map" "test_http_redirect" {
  name = "ielts-genai-prep-test-http-redirect"
  
  default_url_redirect {
    https_redirect         = true
    redirect_response_code = "MOVED_PERMANENTLY_DEFAULT"
    strip_query            = false
  }
}

resource "google_compute_target_http_proxy" "test_http_redirect" {
  name    = "ielts-genai-prep-test-http-proxy"
  url_map = google_compute_url_map.test_http_redirect.id
}

resource "google_compute_global_forwarding_rule" "test_http" {
  name                  = "ielts-genai-prep-test-http"
  ip_protocol           = "TCP"
  load_balancing_scheme = "EXTERNAL_MANAGED"
  port_range            = "80"
  target                = google_compute_target_http_proxy.test_http_redirect.id
  ip_address            = google_compute_global_address.test_ip.id
}

# Outputs
output "test_subdomain_ip" {
  value       = google_compute_global_address.test_ip.address
  description = "IP address for test.ieltsaiprep.com"
}

output "test_cloud_run_url" {
  value       = google_cloud_run_v2_service.test_app.uri
  description = "Direct Cloud Run URL for test environment"
}
