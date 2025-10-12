# Security Notice for Test Credentials

## Important: Test Credentials Have Been Moved to Environment Variables

For security reasons, all test credentials have been removed from the source code and must now be configured via environment variables.

### Setting Up Test Credentials

1. **Copy the environment template:**
   ```bash
   cp .env.example .env
   ```

2. **Edit `.env` and set secure test passwords:**
   ```
   GDPR_TEST_EMAIL=gdpr_test@example.com
   GDPR_TEST_PASSWORD=<your-secure-password>
   
   TEST_USER_EMAIL=test@example.com
   TEST_USER_PASSWORD=<your-secure-password>
   
   MANUAL_TEST_EMAIL=manual@example.com
   MANUAL_TEST_PASSWORD=<your-secure-password>
   ```

3. **For CI/CD (GitHub Actions):**
   Add these as repository secrets in Settings → Secrets and variables → Actions:
   - `GDPR_TEST_PASSWORD`
   - `TEST_USER_PASSWORD`
   - `MANUAL_TEST_PASSWORD`

### Security Best Practices

- **NEVER** commit actual passwords to the repository
- **NEVER** hardcode credentials in test files
- **ALWAYS** use environment variables for sensitive data
- The `.env` file is gitignored and should never be committed
- Use strong, unique passwords even for test accounts

### Running Tests

Tests will automatically use environment variables if set, or fall back to safe defaults that won't pass authentication (forcing you to set real values).

```bash
# Set environment variables and run tests
export TEST_USER_PASSWORD="YourSecurePassword123!"
pytest tests/
```

### GitGuardian Compliance

This change ensures GitGuardian and other security scanners won't flag our repository for containing exposed credentials.