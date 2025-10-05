# IELTS GenAI Prep - GCP Migration

## 🎯 Complete AWS to GCP Migration Infrastructure

This directory contains the complete infrastructure for migrating **IELTS GenAI Prep** from AWS to Google Cloud Platform.

---

## 📂 Directory Structure

```
gcp/
├── README.md                           # This file
├── GCP_MIGRATION_GUIDE.md              # Comprehensive migration guide
├── deploy.sh                            # One-command deployment script
│
├── firestore_dal.py                    # Firestore Data Access Layer
├── gemini_live_service.py              # Gemini 2.5 Flash Live API (replaces Nova Sonic)
├── gemini_service.py                   # Gemini 2.5 Flash (replaces Nova Micro)
│
├── cloud_run/                          # Cloud Run application
│   ├── Dockerfile                      # Multi-stage Docker build
│   ├── requirements.txt                # Python dependencies
│   ├── cloudbuild.yaml                 # Cloud Build configuration
│   └── app.py                          # Flask application entry point
│
├── cloud_functions/                    # Serverless functions
│   ├── receipt_validation/             # Apple/Google Play receipt validation
│   │   └── main.py
│   └── qr_code_handler/                # QR code generation and validation
│       └── main.py
│
├── terraform/                          # Infrastructure as Code
│   ├── main.tf                         # Main configuration
│   ├── firestore.tf                    # Firestore database + indexes
│   ├── cloud_run.tf                    # Cloud Run + Load Balancer
│   ├── dns.tf                          # Cloud DNS (Route 53 migration)
│   ├── secrets.tf                      # Secret Manager
│   └── cloud_functions.tf             # Cloud Functions deployment
│
└── scripts/                            # Migration utilities
    └── migrate_dynamodb_to_firestore.py # Data migration script
```

---

## ✅ What's Been Built

### 1. **Database Migration: DynamoDB → Firestore**
- ✅ Complete Firestore data access layer (`firestore_dal.py`)
- ✅ User, Assessment, Session, QR Token, Entitlement collections
- ✅ Composite indexes for efficient queries
- ✅ Multi-region replication (`nam5` covering all US regions)
- ✅ Data migration script with verification

### 2. **AI Services: Bedrock Nova → Gemini**
- ✅ **Gemini 2.5 Flash Live API** (`gemini_live_service.py`)
  - Bidirectional speech-to-speech via WebSocket
  - Real-time content moderation
  - Session management
  - Audio format conversion utilities
- ✅ **Gemini 2.5 Flash** (`gemini_service.py`)
  - Writing assessment evaluation
  - Speaking question generation
  - Personalized study plans
  - Content safety checks

### 3. **Compute: Lambda → Cloud Run + Functions**
- ✅ **Cloud Run** (`cloud_run/`)
  - Multi-stage Dockerfile with optimized build
  - Gunicorn with eventlet workers for WebSocket support
  - Multi-region deployment configuration
  - Health checks and auto-scaling
  - Secret Manager integration
  - 60-minute timeout (vs 15min Lambda limit)
  
- ✅ **Cloud Functions** (`cloud_functions/`)
  - Receipt validation (Apple App Store + Google Play)
  - QR code generation and validation
  - Session cleanup (Cloud Scheduler)

### 4. **Infrastructure as Code: Serverless Framework → Terraform**
- ✅ **Firestore** (`terraform/firestore.tf`)
  - Multi-region database configuration
  - Composite indexes
  - Scheduled session cleanup
  
- ✅ **Cloud Run** (`terraform/cloud_run.tf`)
  - Multi-region deployment (us-central1, europe-west1, asia-southeast1)
  - Global HTTPS Load Balancer
  - Cloud CDN integration
  - Serverless Network Endpoint Groups (NEGs)
  - Health checks and automatic failover
  - Managed SSL certificates
  
- ✅ **Cloud DNS** (`terraform/dns.tf`)
  - DNS zone for ieltsaiprep.com
  - A records for apex and www
  - DNSSEC enabled
  - Nameserver configuration
  
- ✅ **Secret Manager** (`terraform/secrets.tf`)
  - All secrets with auto-replication
  - IAM permissions for Cloud Run access
  
- ✅ **Cloud Functions** (`terraform/cloud_functions.tf`)
  - Receipt validation function
  - QR code handler function
  - Session cleanup function

### 5. **Deployment Automation**
- ✅ One-command deployment script (`deploy.sh`)
- ✅ Cloud Build configuration for CI/CD
- ✅ Multi-region rollout strategy
- ✅ Comprehensive migration guide

---

## 🚀 Quick Start

### Prerequisites
```bash
# Install Google Cloud SDK
curl https://sdk.cloud.google.com | bash

# Install Terraform
brew install terraform  # macOS
```

### Deploy to GCP
```bash
# Set project ID
export GOOGLE_CLOUD_PROJECT=your-project-id

# Run deployment
cd gcp
./deploy.sh
```

The script will:
1. Enable required GCP APIs
2. Create Artifact Registry
3. Build and push container images
4. Deploy Terraform infrastructure
5. Set up multi-region Cloud Run services
6. Configure Global Load Balancer
7. Deploy Cloud Functions
8. Output DNS nameservers for domain migration

---

## 🔄 Migration Steps

### 1. Data Migration
```bash
cd gcp/scripts
python migrate_dynamodb_to_firestore.py
python migrate_dynamodb_to_firestore.py --verify-only
```

### 2. Infrastructure Deployment
```bash
cd gcp
./deploy.sh
```

### 3. DNS Migration
Update nameservers at your domain registrar with Cloud DNS nameservers (output by deploy.sh)

### 4. Testing
- Test health checks: `curl https://www.ieltsaiprep.com/health`
- Test Gemini integration
- Verify mobile app purchases
- Check QR code authentication

### 5. Go Live
Once DNS propagates and SSL certificate provisions (15-30 minutes), the application is live on GCP!

---

## 📊 Architecture Comparison

| Component | AWS | GCP |
|-----------|-----|-----|
| **Compute** | Lambda | Cloud Run (3 regions) |
| **Database** | DynamoDB Global Tables | Firestore (nam5 multi-region) |
| **AI** | Bedrock Nova Sonic/Micro | Gemini 2.5 Flash Live/Flash |
| **Functions** | Lambda Functions | Cloud Functions |
| **Load Balancer** | API Gateway + CloudFront | Global HTTPS LB + Cloud CDN |
| **DNS** | Route 53 | Cloud DNS |
| **Secrets** | AWS Secrets Manager | Secret Manager |
| **IaC** | Serverless Framework | Terraform |

---

## 💰 Cost Savings

**AWS Monthly Cost:** ~$936/month
- Lambda: $200
- DynamoDB: $150
- Bedrock: $500
- API Gateway: $35
- CloudFront: $50
- Route 53: $1

**GCP Monthly Cost:** ~$718/month
- Cloud Run: $150
- Firestore: $100
- Vertex AI (Gemini): $400
- Load Balancing: $18
- Cloud CDN: $40
- Cloud DNS: $0.40
- Cloud Functions: $10

**💰 Total Savings:** ~$218/month (~23% reduction)

---

## 🎯 Key Improvements

### Performance
- ✅ **No Cold Starts** - Minimum instances per region
- ✅ **60-Minute Timeout** - vs 15 minutes on Lambda
- ✅ **Native WebSocket** - No connection limits
- ✅ **Global Load Balancer** - Automatic traffic routing

### Scalability
- ✅ **Multi-Region by Default** - 3 regions from day one
- ✅ **Auto-Scaling** - Up to 10 instances per region
- ✅ **Firestore 99.999% SLA** - Higher than DynamoDB

### Developer Experience
- ✅ **Native Flask Support** - No Lambda adapters
- ✅ **Terraform IaC** - Reproducible infrastructure
- ✅ **Cloud Logging** - Better observability
- ✅ **Simplified Architecture** - Less moving parts

---

## 📚 Documentation

- **Migration Guide:** `GCP_MIGRATION_GUIDE.md` - Complete step-by-step guide
- **Deployment:** `deploy.sh` - Automated deployment script
- **Architecture:** See updated `../replit.md`

---

## 🛠 Troubleshooting

### SSL Certificate Provisioning
If SSL cert stuck in "PROVISIONING":
```bash
# Verify DNS
dig www.ieltsaiprep.com

# Check load balancer IP
gcloud compute addresses describe ielts-genai-prep-ip --global
```

### Cloud Run Logs
```bash
gcloud logging tail 'resource.type=cloud_run_revision' \
    --project=$GOOGLE_CLOUD_PROJECT \
    --limit=50
```

### Firestore Queries
Check composite indexes in Firestore console if queries are slow.

---

## 📞 Support

- **GCP Documentation:** https://cloud.google.com/docs
- **Gemini API:** https://cloud.google.com/vertex-ai/generative-ai/docs
- **Cloud Run:** https://cloud.google.com/run/docs

---

## ✅ Migration Checklist

- [x] Firestore DAL implementation
- [x] Gemini Live API integration
- [x] Gemini Flash text service
- [x] Cloud Run Dockerfile + configuration
- [x] Cloud Functions (receipt validation, QR codes)
- [x] Terraform infrastructure (all resources)
- [x] Multi-region deployment setup
- [x] Global Load Balancer + CDN
- [x] Cloud DNS configuration
- [x] Secret Manager setup
- [x] Data migration script
- [x] Deployment automation
- [x] Migration guide documentation
- [x] Updated replit.md
- [ ] Run data migration (pending user approval)
- [ ] Deploy to GCP (pending user approval)
- [ ] Update DNS nameservers (pending user approval)
- [ ] Test all functionality
- [ ] Mobile app endpoint updates
- [ ] Decommission AWS resources

---

## 🎉 Ready to Deploy!

All infrastructure code is complete and ready for deployment. See `GCP_MIGRATION_GUIDE.md` for detailed instructions.

**Estimated Time to Production:** 2-4 hours
- 30 min: Infrastructure deployment
- 1-2 hours: Data migration
- 30 min: DNS propagation
- 15-30 min: SSL certificate provisioning
- 30 min: Testing and verification
