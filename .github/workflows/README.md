# CI/CD Pipeline Documentation

## Overview

This CI/CD pipeline provides comprehensive testing and deployment automation for IELTS AI Prep. It runs on every push and pull request to ensure code quality, functionality, and security.

## Pipeline Stages

### 1. Code Quality & Security (Stage 1)
- **Bandit**: Security vulnerability scanning
- **Pylint**: Code quality and style checking
- **Flake8**: PEP 8 compliance checking
- **Safety**: Dependency vulnerability scanning

### 2. Unit Tests (Stage 2)
- Tests individual components in isolation
- Includes code coverage reporting
- Fast execution (< 1 minute)

### 3. Integration Tests (Stage 3)
- Tests Gemini AI service integration
- Tests Firestore database operations
- Requires Google Cloud credentials

### 4. End-to-End Tests (Stage 4)
- Tests complete user workflows
- Uses Playwright for browser automation
- Tests writing and speaking assessment flows

### 5. Performance Tests (Stage 5)
- Benchmark tests for critical functions
- Load testing with Locust
- Performance regression detection

### 6. Security Tests (Stage 6)
- Authentication security tests
- Data protection tests
- OWASP ZAP scanning

### 7. Build & Deploy (Stage 7)
- Builds Docker images
- Deploys to Cloud Run (test environment)
- Only runs on `cicd-pipeline` and `develop` branches

### 8. Smoke Tests (Stage 8)
- Post-deployment health checks
- Critical functionality verification
- External dependency checks

### 9. Test Summary (Stage 9)
- Aggregates all test results
- Generates comprehensive report
- Always runs (even if previous stages fail)

## Required Secrets

Configure these in GitHub repository settings (`Settings > Secrets and variables > Actions`):

```
GOOGLE_CLOUD_PROJECT       # Your GCP project ID
GEMINI_API_KEY            # Gemini API key
GCP_SA_KEY                # GCP service account key (JSON)
TEST_DATABASE_URL         # Test database connection string
```

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

### Run Specific Test Categories

```bash
# Unit tests only
pytest -m unit

# Integration tests
pytest -m integration

# E2E tests
pytest -m e2e

# Performance tests
pytest -m performance

# Security tests
pytest -m security

# Smoke tests
pytest -m smoke
```

### Run with Coverage

```bash
pytest --cov=gcp --cov-report=html
```

### Run Load Tests

```bash
locust -f tests/performance/locustfile.py
```

## Pipeline Triggers

- **Push to main**: Full pipeline + production deployment (manual approval required)
- **Push to develop**: Full pipeline + test environment deployment
- **Push to cicd-pipeline**: Full pipeline + test environment deployment
- **Pull Request**: Full pipeline (no deployment)
- **Manual**: Can be triggered via GitHub Actions UI

## Test Reports

All test runs generate reports available as GitHub Actions artifacts:

- **security-reports**: Bandit, Pylint, Flake8, Safety reports
- **coverage-reports**: Code coverage HTML and XML reports
- **e2e-reports**: End-to-end test results with screenshots
- **performance-reports**: Benchmark and load test results
- **test-summary**: Overall test summary markdown

## Skipping Tests

To skip tests in specific scenarios:

```python
@pytest.mark.skipif(not os.getenv('GEMINI_API_KEY'), reason="API key not set")
def test_requiring_api():
    pass
```

## Best Practices

1. **Write tests first**: Use TDD approach for new features
2. **Keep tests independent**: Each test should be able to run in isolation
3. **Use fixtures**: Leverage pytest fixtures for setup/teardown
4. **Mock external services**: Use mocks for unit tests, real services for integration tests
5. **Document test intent**: Clear test names and docstrings
6. **Monitor performance**: Check benchmark results for regressions
7. **Review coverage**: Aim for >80% code coverage

## Troubleshooting

### Tests failing locally but passing in CI
- Check Python version matches CI (3.11)
- Ensure all dependencies are installed
- Check environment variables

### Integration tests failing
- Verify Google Cloud credentials are set
- Check API quotas and limits
- Ensure test database is accessible

### E2E tests timing out
- Increase timeout values in test
- Check application startup time
- Verify browser automation is working

## Adding New Tests

1. Create test file in appropriate directory:
   - `tests/unit/` for unit tests
   - `tests/integration/` for integration tests
   - `tests/e2e/` for end-to-end tests
   - `tests/performance/` for performance tests
   - `tests/security/` for security tests
   - `tests/smoke/` for smoke tests

2. Follow naming convention: `test_*.py`

3. Use appropriate markers:
   ```python
   @pytest.mark.unit
   def test_something():
       pass
   ```

4. Add test to CI/CD pipeline if needed

## Continuous Improvement

- Regularly review and update tests
- Add tests for bug fixes
- Improve coverage for critical paths
- Monitor test execution time
- Keep dependencies updated
