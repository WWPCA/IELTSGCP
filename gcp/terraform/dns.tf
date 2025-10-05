# Cloud DNS Configuration for www.ieltsaiprep.com
# Migrated from AWS Route 53

# Cloud DNS Managed Zone
resource "google_dns_managed_zone" "ieltsaiprep" {
  name        = "ieltsaiprep-zone"
  dns_name    = "ieltsaiprep.com."
  description = "DNS zone for IELTS AI Prep"
  
  # DNSSEC for security
  dnssec_config {
    state = "on"
  }
}

# A record for apex domain (ieltsaiprep.com) pointing to load balancer
resource "google_dns_record_set" "apex_a" {
  managed_zone = google_dns_managed_zone.ieltsaiprep.name
  name         = "ieltsaiprep.com."
  type         = "A"
  ttl          = 300
  
  rrdatas = [google_compute_global_address.default.address]
}

# A record for www subdomain
resource "google_dns_record_set" "www_a" {
  managed_zone = google_dns_managed_zone.ieltsaiprep.name
  name         = "www.ieltsaiprep.com."
  type         = "A"
  ttl          = 300
  
  rrdatas = [google_compute_global_address.default.address]
}

# CNAME for API subdomain (optional, for future API versioning)
resource "google_dns_record_set" "api_cname" {
  managed_zone = google_dns_managed_zone.ieltsaiprep.name
  name         = "api.ieltsaiprep.com."
  type         = "CNAME"
  ttl          = 300
  
  rrdatas = ["www.ieltsaiprep.com."]
}

# MX records for email (if using custom email)
# resource "google_dns_record_set" "mx" {
#   managed_zone = google_dns_managed_zone.ieltsaiprep.name
#   name         = "ieltsaiprep.com."
#   type         = "MX"
#   ttl          = 3600
#   
#   rrdatas = [
#     "10 mx1.example.com.",
#     "20 mx2.example.com."
#   ]
# }

# TXT record for domain verification
resource "google_dns_record_set" "verification" {
  managed_zone = google_dns_managed_zone.ieltsaiprep.name
  name         = "ieltsaiprep.com."
  type         = "TXT"
  ttl          = 300
  
  rrdatas = [
    "google-site-verification=YOUR_VERIFICATION_CODE"
  ]
}

# SPF record for email security
resource "google_dns_record_set" "spf" {
  managed_zone = google_dns_managed_zone.ieltsaiprep.name
  name         = "ieltsaiprep.com."
  type         = "TXT"
  ttl          = 3600
  
  rrdatas = [
    "v=spf1 include:_spf.google.com ~all"
  ]
}

# Output nameservers for domain registrar update
output "dns_nameservers" {
  value       = google_dns_managed_zone.ieltsaiprep.name_servers
  description = "Update these nameservers at your domain registrar (currently Route 53)"
}

output "dns_zone_id" {
  value = google_dns_managed_zone.ieltsaiprep.id
}
