# Push Updates to GitHub - Command Guide

## 📋 Files Ready to Push

### Updated Files (AWS Architecture):
- ✅ `app.py` - AWS DynamoDB references
- ✅ `deployment/app.py` - AWS DynamoDB references  
- ✅ `dynamodb_dal.py` - DynamoDB data access layer
- ✅ `deployment/dynamodb_dal.py` - DynamoDB DAL for Lambda
- ✅ `receipt_validation.py` - DynamoDB integration
- ✅ `helpdesk_service.py` - DynamoDB comments
- ✅ `gcp/README.md` - Deprecation notice
- ✅ `tests/integration/test_firestore.py` - Marked deprecated

### New Files:
- ✅ `bedrock_service.py` - AWS Bedrock Nova Micro service
- ✅ `deployment/bedrock_service.py` - Bedrock for Lambda
- ✅ `ARCHITECTURE_MIGRATION.md` - Migration documentation
- ✅ `AWS_DEPLOYMENT_SUMMARY.md` - Deployment guide
- ✅ `GITHUB_PUSH_CHECKLIST.md` - Push checklist
- ✅ `LOCAL_VS_REMOTE_STATUS.md` - Local vs remote status

---

## 🚀 Step-by-Step Push Commands

### **Step 1: Open Replit Shell**
Click on the Shell tab in your Replit workspace

### **Step 2: Stage All AWS Architecture Files**
```bash
git add app.py \
  deployment/app.py \
  dynamodb_dal.py \
  deployment/dynamodb_dal.py \
  bedrock_service.py \
  deployment/bedrock_service.py \
  receipt_validation.py \
  helpdesk_service.py \
  gcp/README.md \
  tests/integration/test_firestore.py
```

### **Step 3: Stage Documentation Files**
```bash
git add replit.md \
  ARCHITECTURE_MIGRATION.md \
  AWS_DEPLOYMENT_SUMMARY.md \
  GITHUB_PUSH_CHECKLIST.md \
  LOCAL_VS_REMOTE_STATUS.md \
  PUSH_TO_GITHUB_COMMANDS.md
```

### **Step 4: Stage Deployment Folder (Critical!)**
```bash
# Add the entire deployment package
git add deployment/
```

### **Step 5: Check What Will Be Committed**
```bash
git status
```

### **Step 6: Create Commit**
```bash
git commit -m "feat: Complete AWS architecture migration - DynamoDB + Lambda + Bedrock

- Updated all code references from GCP Firestore to AWS DynamoDB
- Added DynamoDB data access layer (dynamodb_dal.py)
- Added AWS Bedrock Nova Micro service (bedrock_service.py)
- Included complete Lambda deployment package (/deployment folder)
- Updated receipt_validation.py to use DynamoDB instead of Firestore
- Marked GCP migration code as deprecated (gcp/ folder)
- Added comprehensive architecture documentation
- Updated replit.md with current AWS hybrid architecture

Architecture: AWS Lambda + DynamoDB + Bedrock Nova Micro + Google Gemini Flash"
```

### **Step 7: Push to GitHub**

#### **Option A: If you have GitHub credentials configured**
```bash
git push origin ci/comprehensive-testing-pipeline
```

#### **Option B: If you need to use a Personal Access Token**
If the above fails and asks for authentication:

1. **Create a GitHub Personal Access Token** (if you don't have one):
   - Go to: https://github.com/settings/tokens
   - Click "Generate new token (classic)"
   - Select scope: `repo` (full control of private repositories)
   - Copy the token

2. **Store it as a Replit Secret** (optional for future):
   - Click on "Secrets" (lock icon) in left sidebar
   - Create new secret: 
     - Key: `GITHUB_TOKEN`
     - Value: your personal access token

3. **Push with token**:
```bash
# Replace YOUR_TOKEN with your actual token
git push https://YOUR_TOKEN@github.com/WWPCA/IELTSGCP.git ci/comprehensive-testing-pipeline
```

---

## ✅ Verification

After pushing, verify your changes:

1. **Check GitHub**: https://github.com/WWPCA/IELTSGCP/tree/ci/comprehensive-testing-pipeline

2. **Verify these files are present**:
   - `dynamodb_dal.py` ✅
   - `bedrock_service.py` ✅
   - `deployment/` folder ✅
   - Updated `app.py` with AWS references ✅

---

## 🔍 Troubleshooting

### If push is rejected due to conflicts:
```bash
# Pull remote changes first
git pull origin ci/comprehensive-testing-pipeline --rebase

# Then push again
git push origin ci/comprehensive-testing-pipeline
```

### If you need to force push (use with caution):
```bash
git push origin ci/comprehensive-testing-pipeline --force
```

### To check git configuration:
```bash
git config --list
```

---

## 📊 What This Push Accomplishes

**Before (GitHub Remote):**
- ❌ GCP Firestore references
- ❌ Missing AWS infrastructure files
- ❌ Missing Lambda deployment package

**After (This Push):**
- ✅ AWS DynamoDB references throughout
- ✅ Complete AWS infrastructure (DynamoDB + Bedrock)
- ✅ Full Lambda deployment package
- ✅ Comprehensive documentation
- ✅ GCP code properly deprecated

**Result:** GitHub repository will be fully aligned with your AWS architecture!
