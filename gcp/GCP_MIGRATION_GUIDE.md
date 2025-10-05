# GCP Migration Guide: IELTS GenAI Prep
## AWS → Google Cloud Platform Complete Migration

### 📋 Migration Overview

This guide covers the complete migration from AWS to GCP:

| Component | AWS | GCP | Status |
|-----------|-----|-----|--------|
| **Compute** | Lambda + API Gateway | Cloud Run | ✅ Ready |
| **Database** | DynamoDB Global Tables | Firestore (nam5) | ✅ Ready |
| **AI Services** | Bedrock (Nova Sonic/Micro) | Vertex AI (Gemini Live/Flash) | ✅ Ready |
| **Storage** | S3 | Cloud Storage | ✅ Ready |
| **Secrets** | AWS Secrets Manager | Secret Manager | ✅ Ready |
| **DNS** | Route 53 | Cloud DNS | ✅ Ready |
| **CDN** | CloudFront | Cloud CDN | ✅ Ready |
| **Functions** | Lambda Functions | Cloud Functions | ✅ Ready |

---

## 🎯 Migration Architecture

### Multi-Region Deployment
- **Primary Region**: `us-central1` (Iowa)
- **Secondary Regions**: `europe-west1` (Belgium), `asia-southeast1` (Singapore)
- **Database**: Firestore `nam5` (multi-region US - covers all US regions)
- **Load Balancer**: Global HTTPS Load Balancer with Cloud CDN

### Service Mapping

#### 1. **Flask App: AWS Lambda → Cloud Run**
- **Before**: Lambda function with API Gateway
- **After**: Cloud Run service (3 regions) behind Global Load Balancer
- **Benefits**: 
  - True WebSocket support (no connection limits)
  - Longer request timeout (60 minutes vs 15 minutes)
  - Better cold start performance
  - Native Flask support (no Lambda adapters)

#### 2. **Database: DynamoDB → Firestore**
```
DynamoDB Global Tables           →    Firestore Multi-Region
├── users table                 →    ├── users collection
├── assessments table           →    ├── assessments collection
├── sessions table              →    ├── sessions collection
├── qr_tokens table             →    ├── qr_tokens collection
├── entitlements table          →    ├── entitlements collection
└── purchase_receipts table     →    └── (merged with entitlements)
```

**Migration Script**: `scripts/migrate_dynamodb_to_firestore.py`

#### 3. **AI Services: Bedrock → Vertex AI**
```
Nova Sonic (speech-to-speech)   →    Gemini 2.5 Flash Live API
Nova Micro (text generation)    →    Gemini 2.5 Flash
```

**Key Differences**:
- Gemini Live API uses WebSocket (native support in Cloud Run)
- Streaming responses built-in
- Better multilingual support
- Real-time content moderation with Google Cloud Natural Language API

#### 4. **Serverless Functions: Lambda → Cloud Functions**
```
Receipt Validation Lambda       →    receipt-validation Cloud Function
QR Code Handler Lambda          →    qr-code-handler Cloud Function
Session Cleanup (EventBridge)   →    cleanup-sessions (Cloud Scheduler)
```

---

## 🚀 Deployment Steps

### Prerequisites

1. **Google Cloud Project**
   ```bash
   gcloud projects create ielts-genai-prep-prod
   export GOOGLE_CLOUD_PROJECT=ielts-genai-prep-prod
   gcloud config set project $GOOGLE_CLOUD_PROJECT
   ```

2. **Enable Billing**
   - Link billing account in Google Cloud Console

3. **Install Tools**
   ```bash
   # Google Cloud SDK
   curl https://sdk.cloud.google.com | bash
   
   # Terraform
   brew install terraform  # macOS
   # or download from terraform.io
   ```

### Step 1: Data Migration (DynamoDB → Firestore)

```bash
# Export DynamoDB data
cd scripts
python export_dynamodb_data.py

# Import to Firestore
python import_to_firestore.py
```

**Data Validation**:
- Run `python validate_migration.py` to compare record counts
- Check sample records for data integrity

### Step 2: Deploy GCP Infrastructure

```bash
cd gcp

# Set project ID
export GOOGLE_CLOUD_PROJECT=your-project-id

# Run deployment
./deploy.sh
```

The script will:
1. Enable required APIs
2. Create Artifact Registry
3. Build and push container images
4. Deploy Terraform infrastructure (Firestore, Cloud Run, Load Balancer, DNS)
5. Deploy Cloud Functions
6. Output DNS nameservers

### Step 3: Add Secrets to Secret Manager

```bash
# Generate new secrets (recommended for security)
SESSION_SECRET=$(openssl rand -base64 32)
JWT_SECRET=$(openssl rand -base64 32)
QR_ENCRYPTION_KEY=$(openssl rand -base64 32)

# Add to Secret Manager
echo -n "$SESSION_SECRET" | gcloud secrets versions add session-secret --data-file=-
echo -n "$JWT_SECRET" | gcloud secrets versions add jwt-secret --data-file=-
echo -n "$QR_ENCRYPTION_KEY" | gcloud secrets versions add qr-encryption-key --data-file=-

# Copy existing AWS secrets
echo -n "your-recaptcha-secret" | gcloud secrets versions add recaptcha-v2-secret-key --data-file=-
echo -n "your-apple-secret" | gcloud secrets versions add apple-shared-secret --data-file=-
echo -n "your-sendgrid-key" | gcloud secrets versions add sendgrid-api-key --data-file=-

# Google Play service account JSON
cat service-account.json | gcloud secrets versions add google-service-account --data-file=-
```

### Step 4: DNS Migration (Route 53 → Cloud DNS)

#### Get Cloud DNS Nameservers
```bash
cd gcp/terraform
terraform output dns_nameservers
```

Output example:
```
ns-cloud-a1.googledomains.com.
ns-cloud-a2.googledomains.com.
ns-cloud-a3.googledomains.com.
ns-cloud-a4.googledomains.com.
```

#### Update Domain Registrar
1. Go to your domain registrar (e.g., Namecheap, GoDaddy)
2. Replace Route 53 nameservers with Cloud DNS nameservers
3. Save changes

**DNS Propagation**: Wait 24-48 hours for full propagation

#### Test DNS Resolution
```bash
# Check A record
dig www.ieltsaiprep.com

# Check nameservers
dig NS ieltsaiprep.com
```

### Step 5: SSL Certificate Provisioning

Google-managed SSL certificates auto-provision after DNS propagation:

```bash
# Check SSL certificate status
gcloud compute ssl-certificates describe ielts-genai-prep-ssl \
    --global \
    --format="value(managed.status)"
```

Status progression: `PROVISIONING` → `ACTIVE` (~15 minutes after DNS propagation)

### Step 6: Verify Deployment

#### Health Checks
```bash
# Get load balancer IP
LB_IP=$(gcloud compute addresses describe ielts-genai-prep-ip --global --format="value(address)")

# Test health endpoint
curl http://$LB_IP/health

# Test HTTPS (after SSL provisioning)
curl https://www.ieltsaiprep.com/health
```

#### Cloud Run Services
```bash
# List all regional services
gcloud run services list --project=$GOOGLE_CLOUD_PROJECT

# Get logs from primary region
gcloud logging tail 'resource.type=cloud_run_revision' \
    --project=$GOOGLE_CLOUD_PROJECT \
    --limit=50
```

#### Test Gemini Integration
```bash
# Test Gemini Live API (WebSocket)
# Use browser console or WebSocket client

# Test Gemini Flash (text)
curl -X POST https://www.ieltsaiprep.com/api/test-gemini \
    -H "Content-Type: application/json" \
    -d '{"prompt": "Hello Maya"}'
```

---

## 📊 Cost Comparison

### AWS (Current Monthly Cost Estimate)

| Service | Cost |
|---------|------|
| Lambda (10M invocations) | ~$200 |
| DynamoDB Global Tables | ~$150 |
| Bedrock (Nova Sonic/Micro) | ~$500 |
| API Gateway | ~$35 |
| CloudFront | ~$50 |
| Route 53 | ~$1 |
| **Total** | **~$936/month** |

### GCP (Estimated Monthly Cost)

| Service | Cost |
|---------|------|
| Cloud Run (3 regions, 1 min instance each) | ~$150 |
| Firestore (nam5 multi-region) | ~$100 |
| Vertex AI (Gemini Live/Flash) | ~$400 |
| Cloud Load Balancing | ~$18 |
| Cloud CDN | ~$40 |
| Cloud DNS | ~$0.40 |
| Cloud Functions | ~$10 |
| **Total** | **~$718/month** |

**Savings**: ~$218/month (~23% reduction)

---

## 🔄 Rollback Plan

If issues arise, you can quickly rollback to AWS:

### Option 1: DNS Rollback (Fastest)
```bash
# Change DNS back to AWS Load Balancer IP at domain registrar
# Takes 5-15 minutes for propagation
```

### Option 2: Parallel Running
- Keep AWS infrastructure running during GCP migration
- Use DNS weighted routing for gradual traffic shift
- Monitor error rates and latency

---

## 🧪 Testing Checklist

Before going live:

- [ ] Health checks pass in all 3 regions
- [ ] User registration and login working
- [ ] QR code authentication (mobile → web)
- [ ] Apple/Google Play receipt validation
- [ ] Writing assessment submission and grading
- [ ] Speaking assessment with Gemini Live (WebSocket)
- [ ] Email notifications (SendGrid)
- [ ] Mobile app purchases and entitlements
- [ ] Session management and expiration
- [ ] SSL certificate provisioned and valid
- [ ] DNS resolves correctly
- [ ] Load balancer distributing traffic across regions
- [ ] Cloud Run auto-scaling working
- [ ] Firestore queries performing well
- [ ] Cloud Logging capturing errors

---

## 📈 Monitoring & Observability

### Cloud Logging
```bash
# View real-time logs
gcloud logging tail 'resource.type=cloud_run_revision' --project=$GOOGLE_CLOUD_PROJECT

# Filter errors
gcloud logging read 'resource.type=cloud_run_revision AND severity>=ERROR' \
    --limit=50 \
    --project=$GOOGLE_CLOUD_PROJECT
```

### Cloud Monitoring Dashboards
- Cloud Run: Request latency, error rates, instance count
- Firestore: Read/write operations, index usage
- Vertex AI: Gemini API calls, latency, costs
- Load Balancer: Traffic distribution, backend health

### Alerting
Create alerts for:
- Error rate > 1%
- P95 latency > 2 seconds
- Instance count at max capacity
- Firestore quota approaching limits

---

## 🛠 Troubleshooting

### Issue: SSL Certificate Stuck in "PROVISIONING"
**Cause**: DNS not fully propagated or A records incorrect

**Solution**:
```bash
# Verify DNS A records
dig www.ieltsaiprep.com

# Check load balancer IP matches
gcloud compute addresses describe ielts-genai-prep-ip --global
```

### Issue: Cloud Run Cold Starts
**Cause**: No minimum instances configured

**Solution**:
```bash
# Set min instances to 1 per region
gcloud run services update ielts-genai-prep \
    --min-instances=1 \
    --region=us-central1
```

### Issue: Firestore Query Slow
**Cause**: Missing composite index

**Solution**:
- Check error message for required index
- Add index in Firestore Console or via Terraform

### Issue: Gemini API Rate Limiting
**Cause**: Too many concurrent requests

**Solution**:
- Request quota increase in Google Cloud Console
- Implement request queuing in application

---

## 📞 Support Resources

- **GCP Documentation**: https://cloud.google.com/docs
- **Vertex AI Gemini**: https://cloud.google.com/vertex-ai/generative-ai/docs
- **Cloud Run Best Practices**: https://cloud.google.com/run/docs/tips
- **Firestore Documentation**: https://firebase.google.com/docs/firestore
- **Terraform Google Provider**: https://registry.terraform.io/providers/hashicorp/google/latest/docs

---

## ✅ Post-Migration Cleanup

After successful migration (2-4 weeks of stable operation):

1. **Decommission AWS Resources**
   ```bash
   # Delete CloudFormation stacks
   aws cloudformation delete-stack --stack-name ielts-genai-prep-prod
   
   # Delete DynamoDB tables (after data verification)
   # Delete Lambda functions
   # Delete API Gateway
   # Cancel Route 53 hosted zone
   ```

2. **Update Mobile Apps**
   - Update API endpoints in iOS/Android apps
   - Submit new app versions to App Store/Play Store

3. **Update Documentation**
   - Update replit.md with GCP architecture
   - Update deployment guides

---

## 🎉 Migration Complete!

Your IELTS GenAI Prep application is now running on Google Cloud Platform with:
- ✅ Multi-region deployment (3 regions)
- ✅ Improved scalability and performance
- ✅ Cost savings (~23%)
- ✅ Modern AI capabilities (Gemini 2.5 Flash)
- ✅ Enterprise-grade infrastructure
