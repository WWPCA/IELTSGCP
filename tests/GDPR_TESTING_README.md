# GDPR Compliance Testing Guide

## Overview

This test suite verifies GDPR compliance for IELTS AI Prep, covering all data protection rights:
- ✅ Right to Access
- ✅ Right to Data Portability (Export)
- ✅ Right to Erasure (Deletion)
- ✅ Right to Withdraw Consent
- ✅ Privacy Policy Section 8 Compliance

## Test User Creation

### Automated Test User Setup

The registration flow requires mobile app purchase, so we use a test user utility:

```bash
# Create test users
python tests/create_test_user.py create --env test

# Delete test users (cleanup)
python tests/create_test_user.py delete --env test
```

### Test Credentials

Test user credentials must be set as environment variables for security:

1. **Copy the environment template:**
   ```bash
   cp .env.example .env
   ```

2. **Edit `.env` and set secure test passwords**

3. **For CI/CD, add these as GitHub Secrets:**
   - `GDPR_TEST_PASSWORD`
   - `TEST_USER_PASSWORD`
   - `MANUAL_TEST_PASSWORD`
   - `GOOGLE_CLOUD_PROJECT`
   - `GEMINI_API_KEY`

The system creates three test accounts:
- **GDPR Test User**: For automated GDPR compliance tests
- **Test User**: For general automated testing
- **Manual Test User**: For manual QA testing

Note: Passwords are never stored in code for security reasons.

## Running GDPR Tests

### Run All GDPR Tests

```bash
pytest tests/test_gdpr_compliance.py -v -m gdpr
```

### Run Specific Test Classes

```bash
# Test data access rights
pytest tests/test_gdpr_compliance.py::TestGDPRDataAccess -v

# Test data export
pytest tests/test_gdpr_compliance.py::TestGDPRDataExport -v

# Test consent management
pytest tests/test_gdpr_compliance.py::TestGDPRConsentManagement -v

# Test account deletion
pytest tests/test_gdpr_compliance.py::TestGDPRAccountDeletion -v

# Test privacy policy compliance
pytest tests/test_gdpr_compliance.py::TestGDPRPrivacyPolicy -v
```

### Run with Coverage

```bash
pytest tests/test_gdpr_compliance.py --cov=app --cov-report=html
```

## Manual Testing Workflow

Since users can't register without the mobile app, follow this workflow:

### 1. Create Test User
```bash
python tests/create_test_user.py create --env development
```

### 2. Login and Test GDPR Features

1. **Login**: Navigate to `/login`
   - Use the test credentials configured in your `.env` file
   - Default email: `test@example.com` (configurable via TEST_USER_EMAIL)

2. **Access GDPR Dashboard**: Navigate to `/gdpr/my-data`
   - ✅ Verify all personal data is displayed
   - ✅ Check email, username, full name, join date

3. **Test Data Export**:
   - ✅ Click "Download My Data"
   - ✅ Verify JSON file downloads
   - ✅ Verify it contains: personal_information, account_information, consent_preferences, assessment_information
   - ✅ Verify password hash is NOT included

4. **Test Consent Management**:
   - ✅ Toggle marketing consent checkbox
   - ✅ Toggle analytics consent checkbox
   - ✅ Click "Update Consent"
   - ✅ Verify success message
   - ✅ Refresh page and verify preferences are saved

5. **Test Account Deletion**:
   - ✅ Enter password in deletion field
   - ✅ Click "Delete My Account"
   - ✅ Verify confirmation dialog
   - ✅ Confirm deletion
   - ✅ Verify redirect to home page
   - ✅ Try to login - should fail (account deleted)

### 3. Verify Privacy Policy

1. Navigate to `/privacy-policy`
2. ✅ Verify Section 8 "Your Data Protection Rights" exists
3. ✅ Verify all GDPR rights are listed
4. ✅ Verify link to GDPR dashboard (`/gdpr/my-data`)
5. ✅ Verify helpdesk email: `helpdesk@ieltsaiprep.com`
6. ✅ Verify 30-day response commitment

## CI/CD Integration

### GitHub Actions Workflow

Add to `.github/workflows/gdpr-tests.yml`:

```yaml
name: GDPR Compliance Tests

on:
  push:
    branches: [ main, ci/comprehensive-testing-pipeline ]
  pull_request:
    branches: [ main ]

jobs:
  gdpr-tests:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest pytest-cov
    
    - name: Create test users
      env:
        GDPR_TEST_PASSWORD: ${{ secrets.GDPR_TEST_PASSWORD }}
        TEST_USER_PASSWORD: ${{ secrets.TEST_USER_PASSWORD }}
        MANUAL_TEST_PASSWORD: ${{ secrets.MANUAL_TEST_PASSWORD }}
      run: python tests/create_test_user.py create --env test
    
    - name: Run GDPR tests
      run: pytest tests/test_gdpr_compliance.py -v --cov=app --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
    
    - name: Cleanup test users
      if: always()
      run: python tests/create_test_user.py delete --env test
```

## Test Coverage

The test suite covers:

### 1. Authentication & Authorization
- ✅ GDPR routes require authentication
- ✅ Unauthenticated access redirects to login
- ✅ Session validation for all endpoints

### 2. Data Access (Right to Access)
- ✅ My Data dashboard displays user information
- ✅ All personal data visible to user
- ✅ Proper authentication checks

### 3. Data Export (Right to Data Portability)
- ✅ Complete data export in JSON format
- ✅ All data categories included
- ✅ Password hash excluded (security)
- ✅ Export metadata included

### 4. Consent Management (Right to Withdraw Consent)
- ✅ Update marketing consent
- ✅ Update analytics consent
- ✅ Withdraw all consents
- ✅ Preferences persist in database

### 5. Account Deletion (Right to Erasure)
- ✅ Password confirmation required
- ✅ Invalid password rejected
- ✅ Successful deletion removes all data
- ✅ Session cleared after deletion
- ✅ User cannot login after deletion

### 6. Privacy Policy Compliance
- ✅ Section 8 exists and is complete
- ✅ All GDPR rights documented
- ✅ Link to GDPR dashboard
- ✅ Contact information visible
- ✅ 30-day response commitment

## Known Issues & Workarounds

### Issue: Cannot Register Without Mobile App

**Problem**: Users cannot register on the web platform without purchasing through mobile app.

**Workaround**: Use `tests/create_test_user.py` to create test users programmatically.

**For CI/CD**: The test suite automatically creates and cleans up test users.

## Compliance Checklist

- [x] Right to Access implemented
- [x] Right to Data Portability implemented
- [x] Right to Erasure implemented
- [x] Right to Withdraw Consent implemented
- [x] Privacy Policy Section 8 updated
- [x] GDPR dashboard linked in Privacy Policy
- [x] Helpdesk email visible for GDPR requests
- [x] 30-day response commitment documented
- [x] Automated tests covering all GDPR rights
- [x] Test user creation utility for CI/CD
- [x] Manual testing guide provided

## Support

For GDPR-related questions or issues:
- Email: helpdesk@ieltsaiprep.com
- Response time: Within 30 days as required by law
