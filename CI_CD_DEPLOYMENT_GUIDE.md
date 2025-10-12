# CI/CD Pipeline Deployment Guide

## What's Been Created

A comprehensive CI/CD testing pipeline has been set up for IELTS AI Prep with:

### 📁 Test Suite Structure
```
tests/
├── unit/                     # Unit tests (fast, isolated)
│   └── test_gemini_services.py
├── integration/              # Integration tests (real API calls)
│   ├── test_gemini_services.py
│   └── test_firestore.py
├── e2e/                      # End-to-end tests (full workflows)
│   └── test_assessment_flow.py
├── performance/              # Performance & load tests
│   ├── test_benchmarks.py
│   └── locustfile.py
├── security/                 # Security tests
│   └── test_security.py
├── smoke/                    # Post-deployment health checks
│   └── test_smoke.py
└── conftest.py              # Shared test fixtures
```

### 🔧 Configuration Files
- `.github/workflows/ci-cd-testing.yml` - Main CI/CD pipeline
- `.github/workflows/README.md` - Pipeline documentation
- `pytest.ini` - Pytest configuration with test markers
- `requirements-test.txt` - Test dependencies

### 🚀 Pipeline Features
- **9 testing stages**: Code quality → Unit → Integration → E2E → Performance → Security → Build/Deploy → Smoke → Summary
- **Automated deployment** to test environment (test.ieltsaiprep.com)
- **Comprehensive reports**: Security scans, coverage, E2E results, performance benchmarks
- **Multi-environment support**: Test and production workflows

---

## How to Push to GitHub

Since git operations are restricted in Replit, you'll need to push these changes to GitHub yourself. Here's how:

### Step 1: Stage All Changes

```bash
git add .
```

### Step 2: Commit Changes

```bash
git commit -m "Add comprehensive CI/CD testing pipeline

- Add GitHub Actions workflow with 9 testing stages
- Create unit tests for Gemini services
- Add integration tests for Gemini and Firestore
- Create E2E tests with Playwright
- Add performance/load tests with Locust
- Implement security tests
- Add smoke tests for deployment validation
- Update pytest configuration
- Add test dependencies to requirements-test.txt
"
```

### Step 3: Create New Branch (Optional)

If you want to test the pipeline on a separate branch first:

```bash
git checkout -b cicd-pipeline
```

### Step 4: Push to GitHub

Push to main branch:
```bash
git push origin main
```

Or push to new branch:
```bash
git push origin cicd-pipeline
```

---

## GitHub Secrets Configuration

Before the pipeline can run successfully, configure these secrets in your GitHub repository:

1. Go to your repository on GitHub
2. Navigate to **Settings → Secrets and variables → Actions**
3. Click **New repository secret** and add each of the following:

| Secret Name | Description | Where to Get It |
|------------|-------------|-----------------|
| `GOOGLE_CLOUD_PROJECT` | Your GCP project ID | GCP Console → Project Info |
| `GEMINI_API_KEY` | Gemini API key | GCP Console → APIs & Services → Credentials |
| `GCP_SA_KEY` | Service account JSON key | GCP Console → IAM → Service Accounts |
| `TEST_DATABASE_URL` | Test database connection | Your test database URL |

### Creating GCP Service Account Key

```bash
# Create service account
gcloud iam service-accounts create github-actions \
    --display-name="GitHub Actions CI/CD"

# Grant necessary permissions
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
    --member="serviceAccount:github-actions@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/run.admin"

gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
    --member="serviceAccount:github-actions@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/cloudbuild.builds.builder"

# Create and download key
gcloud iam service-accounts keys create key.json \
    --iam-account=github-actions@YOUR_PROJECT_ID.iam.gserviceaccount.com

# Copy the entire contents of key.json and paste into GitHub secret
cat key.json
```

---

## Running the Pipeline

The pipeline will automatically run when you:

1. **Push to main branch** - Full pipeline + manual approval for production
2. **Push to cicd-pipeline branch** - Full pipeline + auto-deploy to test
3. **Create a pull request** - Full pipeline (no deployment)
4. **Manual trigger** - Go to Actions tab → Select workflow → Run workflow

### Viewing Pipeline Results

1. Go to your repository on GitHub
2. Click the **Actions** tab
3. Click on the latest workflow run
4. View each stage's results and logs

### Downloading Reports

After a workflow run completes:

1. Scroll to the bottom of the workflow run page
2. Under **Artifacts**, download:
   - `security-reports` - Bandit, Pylint, Flake8, Safety results
   - `coverage-reports` - Code coverage HTML report
   - `e2e-reports` - End-to-end test results
   - `performance-reports` - Benchmark and load test results
   - `test-summary` - Overall test summary

---

## Running Tests Locally

### Install Test Dependencies

```bash
pip install -r requirements-test.txt
playwright install chromium
```

### Run All Tests

```bash
pytest
```

### Run Specific Test Types

```bash
# Unit tests only (fast)
pytest -m unit

# Integration tests (requires API keys)
pytest -m integration

# E2E tests (requires running app)
pytest -m e2e

# Performance tests
pytest -m performance

# Security tests
pytest -m security

# Smoke tests
pytest -m smoke
```

### Generate Coverage Report

```bash
pytest --cov=gcp --cov-report=html
open htmlcov/index.html
```

---

## Next Steps

1. ✅ **Push changes to GitHub** using the commands above
2. ✅ **Configure GitHub secrets** as detailed in this guide
3. ✅ **Watch the first pipeline run** to ensure everything works
4. ✅ **Review test reports** and fix any issues
5. ✅ **Deploy to test environment** (test.ieltsaiprep.com) for validation
6. ✅ **Add reading comprehension and listening templates** when audio files are ready
7. ✅ **Final testing on test environment** before production launch

---

## Test Coverage Overview

| Test Type | Coverage | Purpose |
|-----------|----------|---------|
| **Unit Tests** | Gemini services, prompt generation | Fast, isolated component testing |
| **Integration Tests** | Real API calls to Gemini, Firestore operations | Verify external service integration |
| **E2E Tests** | Complete user workflows (registration, assessments) | Validate end-user experience |
| **Performance Tests** | Benchmarks, load testing with Locust | Ensure scalability and speed |
| **Security Tests** | Authentication, data protection, XSS/SQL injection | Protect against vulnerabilities |
| **Smoke Tests** | Post-deployment health checks | Verify production deployment |

---

## Troubleshooting

### Pipeline Fails on First Run

- **Check secrets**: Ensure all required secrets are configured correctly
- **Review logs**: Click on failed stage to see detailed error messages
- **API quotas**: Verify Google Cloud API quotas aren't exceeded

### Integration Tests Failing

- **API keys**: Double-check `GEMINI_API_KEY` is valid
- **Project ID**: Verify `GOOGLE_CLOUD_PROJECT` is correct
- **Permissions**: Ensure service account has necessary roles

### E2E Tests Timing Out

- **Increase timeout**: Modify timeout values in `tests/e2e/test_assessment_flow.py`
- **Check app startup**: Ensure Flask app starts within 5 seconds
- **Browser issues**: Playwright may need additional dependencies

### Deployment Failing

- **Service account**: Verify `GCP_SA_KEY` has Cloud Run and Cloud Build permissions
- **Docker build**: Check Dockerfile is present and valid
- **Region availability**: Ensure target region supports Cloud Run

---

## Support

For questions or issues:
1. Check `.github/workflows/README.md` for detailed pipeline documentation
2. Review test files for examples
3. Check GitHub Actions logs for specific error messages

---

## Summary

You now have a **production-ready CI/CD pipeline** that:
- ✅ Automatically tests every code change
- ✅ Ensures code quality and security
- ✅ Validates performance and functionality
- ✅ Deploys to test environment automatically
- ✅ Generates comprehensive reports

**Ready to push!** 🚀
