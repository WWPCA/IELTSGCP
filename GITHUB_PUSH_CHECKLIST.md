# GitHub Push Checklist - AWS Architecture Update

## Overview

This checklist identifies all files that need to be pushed to the GitHub repository (`WWPCA/IELTSGCP`, branch `ci/comprehensive-testing-pipeline`) to reflect the recent migration from GCP to AWS architecture.

**Migration Date:** October 2025  
**Current Branch:** `ci/comprehensive-testing-pipeline`  
**Repository:** https://github.com/WWPCA/IELTSGCP

---

## ✅ Files to Push

### 📁 **Category 1: Core Deployment Package** (CRITICAL)

These files constitute the complete AWS Lambda deployment package that is **currently missing** from the GitHub repository:

- [ ] `deployment/` - **ENTIRE FOLDER** (currently not in GitHub)
  - [ ] `deployment/lambda_handler.py` - Lambda entry point with awsgi wrapper
  - [ ] `deployment/app.py` - Main Flask application (2,051 lines) 
  - [ ] `deployment/bedrock_service.py` - AWS Bedrock Nova Micro service (484 lines)
  - [ ] `deployment/dynamodb_dal.py` - DynamoDB data access layer (435 lines)
  - [ ] `deployment/requirements.txt` - Python dependencies for Lambda
  - [ ] `deployment/templates/` - All HTML templates (60+ files)
  - [ ] `deployment/static/` - All CSS, JS, images, icons
  - [ ] `deployment/[packages]/` - All Python dependencies (flask, boto3, etc.)

**Why Critical:** The entire `/deployment` folder is missing from GitHub. This is the production AWS Lambda package that powers the current infrastructure.

---

### 📝 **Category 2: Architecture Documentation** (HIGH PRIORITY)

New documentation files that explain the architectural changes:

- [ ] `replit.md` - **UPDATED** to reflect AWS architecture (previously showed GCP)
- [ ] `ARCHITECTURE_MIGRATION.md` - **NEW** comprehensive migration guide (GCP → AWS)
- [ ] `AWS_DEPLOYMENT_SUMMARY.md` - **NEW** deployment package documentation
- [ ] `GITHUB_PUSH_CHECKLIST.md` - **NEW** this file

**Why Important:** Documents the architectural shift and provides deployment guidance for the team.

---

### 🔧 **Category 3: AWS Deployment Scripts** (HIGH PRIORITY)

Scripts and templates for AWS infrastructure deployment:

- [ ] `deploy-to-aws-lambda.sh` - Automated Lambda deployment script
- [ ] `deploy-aws-infrastructure.sh` - Complete AWS stack deployment
- [ ] `deploy-cloudformation-stack.sh` - CloudFormation deployment automation
- [ ] `ielts-genai-prep-cloudformation.yaml` - AWS CloudFormation template
- [ ] `requirements-lambda.txt` - Lambda-specific Python requirements
- [ ] `lambda_handler.py` - Root-level Lambda handler (if different from deployment/)

**Why Important:** Enables automated deployment and infrastructure as code for AWS.

---

### 🌐 **Category 4: AWS Configuration Files** (MEDIUM PRIORITY)

Supporting configuration and documentation:

- [ ] `aws-route53-deployment.md` - Route 53 DNS setup guide
- [ ] `aws-dns-migration-complete.sh` - DNS migration script
- [ ] `complete-aws-route53-setup.sh` - Complete Route 53 setup
- [ ] `AWS_DEPLOYMENT_GUIDE.md` - General AWS deployment guide
- [ ] `AWS_LAMBDA_DEPLOYMENT_GUIDE.md` - Lambda-specific deployment guide
- [ ] `cloudformation-console-deployment.md` - Console deployment instructions
- [ ] `aws-deployment-status.md` - Current deployment status
- [ ] `custom-domain-only-template.yaml` - Custom domain CloudFormation template
- [ ] `import-template.yaml` - Resource import template
- [ ] `import-resources-to-existing-stack.md` - Stack import guide
- [ ] `minimal-template.yaml` - Minimal CloudFormation template

**Why Useful:** Provides comprehensive deployment options and troubleshooting guides.

---

### 🤖 **Category 5: Gemini Smart Selection Files** (HIGH PRIORITY)

Files related to the Gemini Flash Lite/Flash smart selection for speaking assessments:

- [ ] `gemini_live_audio_service_smart.py` - Gemini smart selection service (444 lines)
- [ ] `ielts_workflow_manager.py` - IELTS workflow and smart orchestration
- [ ] `hybrid_integration_routes_smart.py` - Hybrid route handlers with smart selection
- [ ] `SMART_SELECTION_FINAL.md` - Smart selection documentation
- [ ] `HYBRID_IMPLEMENTATION_SUMMARY.md` - Hybrid architecture summary
- [ ] `HYBRID_ARCHITECTURE.md` - Hybrid architecture details

**Why Important:** These files implement the cost-saving smart selection between Gemini Flash Lite (Part 1) and Flash (Parts 2-3), achieving 58% cost reduction.

---

### 📊 **Category 6: Testing & Validation** (MEDIUM PRIORITY)

Test files for validating AWS services:

- [ ] `test-aws-domains.py` - AWS domain testing
- [ ] `test_gemini_service.py` - Gemini service testing
- [ ] `quick_gemini_test.py` - Quick Gemini validation
- [ ] `gemini_usage_example.py` - Gemini usage examples

**Why Useful:** Helps validate AWS and Gemini integrations work correctly.

---

### 📦 **Category 7: AWS SAM/Build Artifacts** (OPTIONAL)

Build artifacts from AWS SAM (may want to exclude from git):

- [ ] `.aws-sam/` - AWS SAM build directory (consider adding to .gitignore)
- [ ] `ielts-ai-prep-lambda.zip` - Packaged Lambda deployment (consider excluding)
- [ ] `awscliv2.zip` - AWS CLI installer (consider excluding)

**Why Optional:** These are build artifacts that can be regenerated. Consider excluding from version control.

---

### 📋 **Category 8: Migration & Restoration Scripts** (MEDIUM PRIORITY)

Scripts related to migration and potential rollback:

- [ ] `AWS_RESTORATION_PLAN.md` - Rollback plan if needed
- [ ] `restore_domain_access.py` - Domain access restoration
- [ ] `restore_july_8_functionality.py` - Historical restoration script

**Why Useful:** Provides rollback options and historical reference.

---

## 🚫 Files to EXCLUDE (.gitignore)

These files should NOT be pushed to GitHub (add to `.gitignore` if not already there):

```gitignore
# AWS Build Artifacts
.aws-sam/
*.zip
awscliv2.zip
ielts-ai-prep-lambda.zip

# Python
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
*.so

# Environment
.env
.env.local
*.key
*.pem

# IDE
.vscode/
.idea/
*.swp
*.swo

# Logs
*.log
access_logs/

# Instance data
instance/

# OS
.DS_Store
Thumbs.db
```

---

## 📝 Recommended Commit Strategy

### Commit 1: Core Deployment Package
```bash
git add deployment/
git commit -m "Add AWS Lambda deployment package with DynamoDB and Bedrock integration

- Complete Flask application configured for Lambda
- AWS Bedrock Nova Micro service for writing/reading/listening assessment
- DynamoDB data access layer with User, Session, Assessment, QRToken DALs
- All templates and static assets included
- Dependencies packaged for Lambda deployment"
```

### Commit 2: Architecture Documentation
```bash
git add replit.md ARCHITECTURE_MIGRATION.md AWS_DEPLOYMENT_SUMMARY.md GITHUB_PUSH_CHECKLIST.md
git commit -m "Update architecture documentation to reflect AWS migration

- Update replit.md with AWS infrastructure details
- Add comprehensive migration guide (GCP → AWS)
- Add AWS deployment package documentation
- Add GitHub push checklist for tracking updates"
```

### Commit 3: Deployment Scripts & Templates
```bash
git add deploy-*.sh *.yaml requirements-lambda.txt lambda_handler.py
git commit -m "Add AWS deployment automation scripts and CloudFormation templates

- Lambda deployment automation
- CloudFormation infrastructure templates
- Route 53 DNS configuration scripts
- Requirements for Lambda environment"
```

### Commit 4: Gemini Smart Selection
```bash
git add gemini_live_audio_service_smart.py ielts_workflow_manager.py hybrid_integration_routes_smart.py SMART_SELECTION_FINAL.md HYBRID_*.md
git commit -m "Implement Gemini Smart Selection for cost-optimized speaking assessment

- Smart model switching (Flash Lite for Part 1, Flash for Parts 2-3)
- IELTS workflow manager for part-based orchestration
- Hybrid integration routes with smart selection
- Achieves 58% cost reduction on Gemini usage"
```

### Commit 5: AWS Configuration & Guides
```bash
git add aws-*.md aws-*.sh AWS_*.md cloudformation-*.md custom-domain-*.yaml import-*.yaml minimal-*.yaml
git commit -m "Add AWS configuration files and deployment guides

- Route 53 DNS setup documentation
- CloudFormation deployment guides
- Custom domain templates
- Import and minimal templates for flexible deployment"
```

### Commit 6: Testing & Validation
```bash
git add test-aws-domains.py test_gemini_service.py quick_gemini_test.py gemini_usage_example.py
git commit -m "Add testing scripts for AWS and Gemini service validation

- AWS domain configuration tests
- Gemini service integration tests
- Quick validation and usage examples"
```

---

## 🎯 Pre-Push Validation Checklist

Before pushing to GitHub, verify:

- [ ] **Secrets Removed:** No API keys, passwords, or secrets in any files
- [ ] **Large Files:** Check for files >100MB (GitHub limit)
- [ ] **Dependencies:** Ensure deployment/requirements.txt is accurate
- [ ] **Documentation:** All new docs are complete and accurate
- [ ] **.gitignore Updated:** Exclude build artifacts and sensitive files
- [ ] **Tests Pass:** Run basic tests to ensure nothing is broken
- [ ] **Code Review:** Review key changes before pushing

---

## 🔍 Files Already in GitHub (No Action Needed)

These files are already present in the GitHub repository and don't need updates:

- ✅ `templates/` (root) - Already in GitHub
- ✅ `static/` (root) - Already in GitHub
- ✅ `gcp/` - GCP files (archived, not deleted)
- ✅ `android/` - Android app files
- ✅ `ios/` - iOS app files
- ✅ `tests/` - Test suites
- ✅ `.github/workflows/` - CI/CD workflows

---

## 📊 Summary Statistics

### Files to Push
- **Critical Priority:** 1 complete folder (deployment/) + 4 docs = ~100+ files
- **High Priority:** 10 files (scripts, smart selection)
- **Medium Priority:** 15 files (guides, configs, tests)
- **Optional:** 3 files (build artifacts - consider excluding)

### Estimated Changes
- **New Files:** ~120 files (mostly in deployment/)
- **Updated Files:** 1 file (replit.md)
- **Total Lines of Code:** ~5,000+ lines

### Repository Impact
- **Current Repository Size:** Estimated 50-100 MB
- **After Push:** Estimated 100-150 MB
- **Deploy Package Size:** ~45 MB (deployment/ folder when zipped)

---

## 🚀 Quick Push Commands

After validation, push everything at once:

```bash
# Stage all critical files
git add deployment/
git add replit.md ARCHITECTURE_MIGRATION.md AWS_DEPLOYMENT_SUMMARY.md GITHUB_PUSH_CHECKLIST.md
git add deploy-*.sh *.yaml requirements-lambda.txt
git add gemini_live_audio_service_smart.py ielts_workflow_manager.py hybrid_integration_routes_smart.py
git add aws-*.md AWS_*.md cloudformation-*.md
git add test-aws-domains.py test_gemini_service.py

# Create comprehensive commit
git commit -m "Complete AWS architecture migration with Lambda, DynamoDB, and Gemini Smart Selection

Major Changes:
- Add complete AWS Lambda deployment package (/deployment folder)
- Migrate from GCP Firestore to AWS DynamoDB
- Implement Gemini Smart Selection (58% cost reduction)
- Add CloudFormation templates and deployment automation
- Update architecture documentation to reflect AWS infrastructure

Infrastructure:
- AWS Lambda with DynamoDB for serverless compute and storage
- AWS Bedrock Nova Micro for cost-effective text assessment
- Google Gemini Flash Lite/Flash smart selection for speaking
- CloudFront CDN and Route 53 DNS configuration

Cost Optimization:
- Infrastructure: 67% reduction ($210 → $70/month)
- AI Services: 58% reduction on Gemini (smart model switching)
- Total: 59% overall cost savings

See ARCHITECTURE_MIGRATION.md and AWS_DEPLOYMENT_SUMMARY.md for details."

# Push to GitHub
git push origin ci/comprehensive-testing-pipeline
```

---

## ✅ Post-Push Actions

After successfully pushing to GitHub:

1. **Verify on GitHub:**
   - Visit https://github.com/WWPCA/IELTSGCP/tree/ci/comprehensive-testing-pipeline
   - Confirm `/deployment` folder is visible
   - Check documentation files are rendered correctly

2. **Update Pull Request:**
   - If PR exists, update description with migration details
   - Link to ARCHITECTURE_MIGRATION.md for reviewers

3. **Notify Team:**
   - Inform team about architectural changes
   - Share deployment documentation
   - Schedule review session if needed

4. **CI/CD Update:**
   - Update GitHub Actions workflows for AWS deployment
   - Add secrets to GitHub repository settings (if using CI/CD)
   - Test automated deployment pipeline

---

## 📞 Support & Questions

If you encounter issues during the push:

1. **Large File Issues:** Check `.gitignore` and exclude build artifacts
2. **Merge Conflicts:** Pull latest changes first: `git pull origin ci/comprehensive-testing-pipeline`
3. **Permission Issues:** Ensure you have write access to the repository
4. **Size Warnings:** GitHub has a 100MB per-file limit and 5GB repo limit

---

**Last Updated:** October 12, 2025  
**Migration Status:** ✅ Complete, Ready to Push  
**Estimated Push Time:** 5-10 minutes (depending on connection speed)
