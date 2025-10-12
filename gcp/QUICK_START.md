# 🚀 Quick Start: Deploy to GCP

## ✅ What's Ready

All infrastructure code is complete and ready to deploy:
- ✅ Multi-region Cloud Run (3 regions)
- ✅ Firestore database with indexes
- ✅ Gemini 2.5 Flash integration
- ✅ Global Load Balancer + CDN
- ✅ Cloud DNS configuration
- ✅ Test subdomain (test.ieltsaiprep.com)
- ✅ Cloud Functions (receipts, QR codes)

---

## 🎯 Deploy Test Environment First

Deploy to **test.ieltsaiprep.com** for UI/pricing preview:

```bash
cd gcp
export GOOGLE_CLOUD_PROJECT=your-project-id
./deploy_test.sh
```

This deploys:
- ✅ Single-region Cloud Run (us-central1)
- ✅ Test subdomain (test.ieltsaiprep.com)
- ✅ Firestore database
- ✅ All your current routes and templates

**Time:** ~10-15 minutes
**Cost:** ~$5/month (scales to zero when idle)

---

## 📊 Test Environment Features

- **URL:** https://test.ieltsaiprep.com
- **Direct Cloud Run URL:** Provided after deployment
- **Scales to Zero:** Saves costs when not in use
- **Separate Database:** Uses same Firestore but with "test" prefix
- **Full Features:** All routes from your current app.py

---

## 🔄 Data Migration (When Ready)

After test environment is working:

```bash
# Install GCP SDK on your local machine (not Replit)
# https://cloud.google.com/sdk/docs/install

# Authenticate
gcloud auth login
gcloud config set project your-project-id

# Run migration
cd gcp/scripts
python migrate_dynamodb_to_firestore.py

# Verify
python migrate_dynamodb_to_firestore.py --verify-only
```

**What gets migrated:**
- ✅ Users (email, password hashes, profiles)
- ✅ Assessments (speaking, writing results)
- ✅ Sessions (active web sessions)
- ✅ QR Tokens (authentication tokens)
- ✅ Entitlements (in-app purchases)

---

## 🌐 Full Production Deployment

Once test environment is approved:

```bash
cd gcp
./deploy.sh
```

This deploys:
- ✅ Multi-region Cloud Run (3 regions worldwide)
- ✅ Global HTTPS Load Balancer
- ✅ www.ieltsaiprep.com (production domain)
- ✅ Cloud Functions
- ✅ Full infrastructure

**Time:** ~30-60 minutes
**DNS Update:** Required (nameservers)

---

## 📝 Pre-Deployment Checklist

Before deploying:

- [ ] Google Cloud Project created
- [ ] Billing enabled
- [ ] Domain registrar access (for nameservers)
- [ ] Secrets ready:
  - SESSION_SECRET
  - RECAPTCHA_V2_SECRET_KEY
  - APPLE_SHARED_SECRET
  - GOOGLE_SERVICE_ACCOUNT_JSON
  - JWT_SECRET
  - QR_ENCRYPTION_KEY
  - SENDGRID_API_KEY

---

## 🔐 Adding Secrets

After infrastructure deployment, add secrets:

```bash
# Generate new secrets for GCP (recommended)
SESSION_SECRET=$(openssl rand -base64 32)
JWT_SECRET=$(openssl rand -base64 32)
QR_ENCRYPTION_KEY=$(openssl rand -base64 32)

# Add to Secret Manager
echo -n "$SESSION_SECRET" | gcloud secrets versions add session-secret --data-file=-
echo -n "$JWT_SECRET" | gcloud secrets versions add jwt-secret --data-file=-
echo -n "$QR_ENCRYPTION_KEY" | gcloud secrets versions add qr-encryption-key --data-file=-

# Add existing secrets (copy from AWS)
echo -n "your-recaptcha-secret" | gcloud secrets versions add recaptcha-v2-secret-key --data-file=-
echo -n "your-apple-secret" | gcloud secrets versions add apple-shared-secret --data-file=-
echo -n "your-sendgrid-key" | gcloud secrets versions add sendgrid-api-key --data-file=-

# Google Play service account (JSON file)
cat service-account.json | gcloud secrets versions add google-service-account --data-file=-
```

---

## 🧪 Testing Test Environment

After deployment:

### 1. Health Check
```bash
curl https://test.ieltsaiprep.com/health
# or
curl <CLOUD_RUN_URL>/health
```

### 2. Test Routes
- Homepage: https://test.ieltsaiprep.com/
- Login: https://test.ieltsaiprep.com/login
- Products: https://test.ieltsaiprep.com/assessment-products

### 3. Mobile App Testing
Update mobile app API endpoint to test Cloud Run URL

---

## 🆘 Troubleshooting

### SSL Certificate Pending
```bash
# Check status
gcloud compute ssl-certificates describe ielts-genai-prep-test-ssl \
    --global \
    --format="value(managed.status)"
```
**Solution:** Wait 15-30 minutes after DNS propagation

### Cloud Run Not Starting
```bash
# Check logs
gcloud logging tail 'resource.type=cloud_run_revision' \
    --project=$GOOGLE_CLOUD_PROJECT \
    --limit=50
```

### Firestore Connection Issues
**Solution:** Ensure service account has `roles/datastore.user` permission

---

## 💰 Cost Estimates

### Test Environment
- Cloud Run (scales to zero): ~$0-5/month
- Firestore (minimal data): ~$1/month
- Load Balancer: ~$18/month
- **Total:** ~$20-25/month

### Production Environment
- Cloud Run (3 regions, min 1 instance each): ~$150/month
- Firestore (nam5 multi-region): ~$100/month
- Gemini API: ~$400/month (usage-based)
- Load Balancer + CDN: ~$60/month
- **Total:** ~$710-720/month

---

## 📞 Support

- **Migration Guide:** `GCP_MIGRATION_GUIDE.md`
- **Full README:** `README.md`
- **GCP Docs:** https://cloud.google.com/docs

---

## ✅ Next Steps

1. Deploy test environment: `./deploy_test.sh`
2. Test UI and pricing on test.ieltsaiprep.com
3. Finalize product/pricing changes
4. Migrate data when ready
5. Deploy to production: `./deploy.sh`

**Ready to start? Run `./deploy_test.sh`!** 🚀
