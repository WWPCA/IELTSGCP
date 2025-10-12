# Test Environment Isolation Guide

## 🔒 How Test and Production Are Isolated

### Same GCP Project, Isolated Data

**Why Same Project?**
- Simpler setup (no need for separate billing)
- Easier testing (same secrets, same APIs enabled)
- Lower cost (avoid duplicate infrastructure)

**How Isolation Works:**

### 1. **Firestore Collection Prefixes**

```
Production Collections:
- users/
- assessments/
- sessions/
- qr_tokens/
- entitlements/

Test Collections:
- test_users/
- test_assessments/
- test_sessions/
- test_qr_tokens/
- test_entitlements/
```

**Implementation:**
- `ENVIRONMENT=test` env var in test Cloud Run
- Firestore DAL automatically adds `test_` prefix
- No code changes needed - fully transparent

### 2. **Separate Cloud Run Services**

```
Production:
- ielts-genai-prep (3 regions)
- www.ieltsaiprep.com

Test:
- ielts-genai-prep-test (1 region)
- test.ieltsaiprep.com
```

### 3. **Shared Resources (Intentional)**

These are safely shared between environments:
- ✅ **Secrets** - Same credentials for Apple/Google Play
- ✅ **Gemini API** - Billed to same project
- ✅ **Cloud Functions** - Stateless, safe to share

---

## 🧪 Testing Workflow

### 1. Deploy Test Environment
```bash
cd gcp
./deploy_test.sh
```

### 2. Test URLs
- **Direct:** https://ielts-genai-prep-test-XXXX-uc.a.run.app
- **Custom:** https://test.ieltsaiprep.com

### 3. Create Test Data
All data automatically goes to `test_*` collections:
```python
# When ENVIRONMENT=test
user_dal.create_user(...)  # → saves to test_users/
assessment_dal.create_assessment(...)  # → saves to test_assessments/
```

### 4. Verify Isolation
```bash
# Check Firestore collections in GCP Console
# You should see both:
- users/ (production)
- test_users/ (test)
```

---

## 🚀 Promoting Test to Production

When test looks good:

### 1. Deploy Production
```bash
cd gcp
./deploy.sh
```

### 2. Data Migration
```bash
# Migrate AWS DynamoDB → Firestore production collections
python scripts/migrate_dynamodb_to_firestore.py
```

### 3. DNS Update
Update nameservers at domain registrar

### 4. Cleanup Test Data (Optional)
```bash
# Delete test collections if no longer needed
# (Keeps costs down)
```

---

## 💰 Cost Impact

**With Shared Project:**
- Test Cloud Run: ~$5/month (scales to zero)
- Test data storage: ~$0.10/month (minimal data)
- **Total added cost:** ~$5-10/month

**Savings vs Separate Project:**
- No duplicate NAT gateway ($60/month)
- No duplicate load balancer ($18/month)
- No duplicate DNS zone ($0.40/month)
- **Savings:** ~$78/month

---

## 🔐 Security Considerations

### Safe to Share
- ✅ API keys (Apple, Google Play, SendGrid)
- ✅ Gemini API access
- ✅ reCAPTCHA keys

### Separate in Production
For true enterprise setups, consider separate projects if you need:
- Different billing accounts
- Strict regulatory compliance
- Different IAM policies per environment

---

## 🛠 Advanced: Full Isolation (Optional)

If you need complete separation later:

### 1. Create Separate GCP Project
```bash
gcloud projects create ielts-test
gcloud projects create ielts-prod
```

### 2. Deploy Independently
```bash
# Test
export GOOGLE_CLOUD_PROJECT=ielts-test
./deploy.sh

# Production
export GOOGLE_CLOUD_PROJECT=ielts-prod
./deploy.sh
```

### 3. Separate Firestore Databases
Each project gets its own Firestore instance

**Cost Impact:** +$100-200/month for duplicate infrastructure

---

## ✅ Current Setup Recommendation

**Keep using shared project with collection prefixes:**
- ✅ Simple and cost-effective
- ✅ Easy to manage
- ✅ Perfect for pre-launch testing
- ✅ Can migrate to separate projects later if needed

**When to separate:**
- After launch with significant user base
- If regulatory compliance requires it
- If different teams manage test vs prod

---

## 📞 Questions?

See `QUICK_START.md` for deployment instructions or `GCP_MIGRATION_GUIDE.md` for full details.
