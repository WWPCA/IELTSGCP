# Cloud Run Multi-Region Deployment Configuration

locals {
  all_regions = concat([var.primary_region], var.secondary_regions)
}

# Cloud Run services in each region
resource "google_cloud_run_v2_service" "app" {
  for_each = toset(local.all_regions)
  
  name     = "ielts-genai-prep"
  location = each.key
  
  template {
    service_account = google_service_account.app_service_account.email
    
    scaling {
      min_instance_count = 1
      max_instance_count = 10
    }
    
    containers {
      image = "${var.primary_region}-docker.pkg.dev/${var.project_id}/ielts-genai-prep/app:latest"
      
      ports {
        container_port = 5000
      }
      
      resources {
        limits = {
          cpu    = "2"
          memory = "1Gi"
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
        value = each.key
      }
      
      # Secrets from Secret Manager
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
      
      # Startup probe
      startup_probe {
        http_get {
          path = "/health"
          port = 5000
        }
        initial_delay_seconds = 0
        timeout_seconds       = 1
        period_seconds        = 3
        failure_threshold     = 10
      }
      
      # Liveness probe
      liveness_probe {
        http_get {
          path = "/health"
          port = 5000
        }
        initial_delay_seconds = 10
        timeout_seconds       = 1
        period_seconds        = 10
        failure_threshold     = 3
      }
    }
    
    timeout = "3600s"  # 60 minutes for long-running WebSocket connections
    
    max_instance_request_concurrency = 80
  }
  
  traffic {
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
    percent = 100
  }
  
  depends_on = [google_project_service.required_apis]
}

# Allow unauthenticated access
resource "google_cloud_run_service_iam_member" "public_access" {
  for_each = toset(local.all_regions)
  
  service  = google_cloud_run_v2_service.app[each.key].name
  location = each.key
  role     = "roles/run.invoker"
  member   = "allUsers"
}

# Global Load Balancer for multi-region traffic distribution
resource "google_compute_global_address" "default" {
  name = "ielts-genai-prep-ip"
}

# Backend service with regional NEGs
resource "google_compute_backend_service" "default" {
  name = "ielts-genai-prep-backend"
  
  protocol    = "HTTP"
  port_name   = "http"
  timeout_sec = 3600
  
  # Enable Cloud CDN
  enable_cdn = true
  cdn_policy {
    cache_mode = "CACHE_ALL_STATIC"
    default_ttl = 3600
    client_ttl  = 3600
    max_ttl     = 86400
  }
  
  # Health check
  health_checks = [google_compute_health_check.default.id]
  
  # Load balancing
  load_balancing_scheme = "EXTERNAL_MANAGED"
  
  # Session affinity for WebSocket
  session_affinity = "CLIENT_IP"
  affinity_cookie_ttl_sec = 3600
  
  # Regional backends (Serverless NEGs for each Cloud Run service)
  dynamic "backend" {
    for_each = toset(local.all_regions)
    
    content {
      group           = google_compute_region_network_endpoint_group.cloud_run_neg[backend.value].id
      balancing_mode  = "UTILIZATION"
      capacity_scaler = 1.0
    }
  }
}

# Network Endpoint Groups for Cloud Run services
resource "google_compute_region_network_endpoint_group" "cloud_run_neg" {
  for_each = toset(local.all_regions)
  
  name                  = "ielts-genai-prep-neg-${each.key}"
  network_endpoint_type = "SERVERLESS"
  region                = each.key
  
  cloud_run {
    service = google_cloud_run_v2_service.app[each.key].name
  }
}

# Health check
resource "google_compute_health_check" "default" {
  name               = "ielts-genai-prep-health-check"
  check_interval_sec = 10
  timeout_sec        = 5
  
  http_health_check {
    port         = 5000
    request_path = "/health"
  }
}

# URL map
resource "google_compute_url_map" "default" {
  name            = "ielts-genai-prep-url-map"
  default_service = google_compute_backend_service.default.id
}

# HTTP to HTTPS redirect
resource "google_compute_url_map" "http_redirect" {
  name = "ielts-genai-prep-http-redirect"
  
  default_url_redirect {
    https_redirect         = true
    redirect_response_code = "MOVED_PERMANENTLY_DEFAULT"
    strip_query            = false
  }
}

# SSL certificate (managed by Google)
resource "google_compute_managed_ssl_certificate" "default" {
  name = "ielts-genai-prep-ssl"
  
  managed {
    domains = [var.domain_name, "ieltsaiprep.com"]
  }
}

# HTTPS target proxy
resource "google_compute_target_https_proxy" "default" {
  name             = "ielts-genai-prep-https-proxy"
  url_map          = google_compute_url_map.default.id
  ssl_certificates = [google_compute_managed_ssl_certificate.default.id]
}

# HTTP target proxy (for redirect)
resource "google_compute_target_http_proxy" "http_redirect" {
  name    = "ielts-genai-prep-http-proxy"
  url_map = google_compute_url_map.http_redirect.id
}

# Global forwarding rules
resource "google_compute_global_forwarding_rule" "https" {
  name                  = "ielts-genai-prep-https-rule"
  ip_protocol           = "TCP"
  load_balancing_scheme = "EXTERNAL_MANAGED"
  port_range            = "443"
  target                = google_compute_target_https_proxy.default.id
  ip_address            = google_compute_global_address.default.id
}

resource "google_compute_global_forwarding_rule" "http" {
  name                  = "ielts-genai-prep-http-rule"
  ip_protocol           = "TCP"
  load_balancing_scheme = "EXTERNAL_MANAGED"
  port_range            = "80"
  target                = google_compute_target_http_proxy.http_redirect.id
  ip_address            = google_compute_global_address.default.id
}

# Outputs
output "cloud_run_services" {
  value = {
    for region in local.all_regions :
    region => google_cloud_run_v2_service.app[region].uri
  }
}

output "load_balancer_ip" {
  value = google_compute_global_address.default.address
}

output "ssl_certificate_status" {
  value = google_compute_managed_ssl_certificate.default.managed
}
