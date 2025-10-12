# AWS Deployment Summary

## Overview

This document provides a comprehensive guide to the AWS Lambda deployment package and infrastructure for the IELTS AI Prep platform. The `/deployment` folder contains everything needed to run the application on AWS Lambda.

## Deployment Package Structure

### Complete File Tree

```
/deployment/
├── lambda_handler.py          # Lambda entry point with awsgi wrapper
├── app.py                      # Main Flask application (2,051 lines)
├── bedrock_service.py          # AWS Bedrock Nova Micro integration
├── dynamodb_dal.py             # DynamoDB data access layer
├── requirements.txt            # Python dependencies
│
├── templates/                  # All Jinja2 HTML templates
│   ├── layout.html
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── profile.html
│   ├── assessment_structure/
│   ├── assessments/
│   ├── practice/
│   ├── admin/
│   ├── gdpr/
│   └── errors/
│
├── static/                     # Frontend assets
│   ├── css/
│   │   ├── style.css
│   │   ├── cookie-consent.css
│   │   └── qr-purchase-modal.css
│   ├── js/
│   │   ├── main.js
│   │   ├── speaking.js
│   │   ├── practice.js
│   │   ├── mobile_api_client.js
│   │   └── [8 more JS files]
│   ├── images/
│   ├── audio/
│   └── icons/
│
└── [Python packages]           # All dependencies packaged
    ├── flask/
    ├── flask_login/
    ├── flask_cors/
    ├── werkzeug/
    ├── jinja2/
    ├── boto3/
    ├── botocore/
    ├── bcrypt/
    ├── qrcode/
    └── awsgi/
```

### Key Files Explained

#### 1. `lambda_handler.py` - Lambda Entry Point

```python
"""
Lambda Handler for IELTS AI Prep Flask Application
Wraps Flask app using awsgi for Lambda compatibility
"""
import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from app import app
import awsgi

def handler(event, context):
    """Main Lambda handler - converts API Gateway events to WSGI"""
    return awsgi.response(app, event, context)

if __name__ == "__main__":
    app.run(debug=True, port=5000)  # Local testing
```

**Purpose:** Converts AWS API Gateway events to WSGI requests that Flask can understand.

#### 2. `app.py` - Main Application (2,051 lines)

**Key Components:**
- Flask application initialization with ProxyFix middleware
- AWS DynamoDB integration with fallback to mock services
- AWS Bedrock service initialization
- Gemini Smart Selection for speaking assessments
- User authentication and session management
- All route handlers for:
  - Authentication (login, register, password reset)
  - Assessments (speaking, writing, reading, listening)
  - Practice modules
  - QR code authentication
  - Mobile API endpoints
  - Admin dashboard
  - GDPR compliance

**AWS Integration:**
```python
from dynamodb_dal import DynamoDBConnection, UserDAL, SessionDAL, AssessmentDAL
from bedrock_service import BedrockService

environment = os.environ.get('ENVIRONMENT', 'production')
db_connection = DynamoDBConnection(environment=environment)
bedrock_service = BedrockService()
```

#### 3. `bedrock_service.py` - AWS Bedrock Integration

**Capabilities:**
- Writing assessment with Nova Micro
- Reading comprehension evaluation
- Listening comprehension evaluation
- Official IELTS band score calculation
- Detailed feedback generation

**Cost Efficiency:**
- Writing: ~$0.003 per assessment
- Reading: ~$0.001 per assessment
- Listening: ~$0.001 per assessment

**Example Usage:**
```python
bedrock_service = BedrockService(region='us-east-1')

evaluation = bedrock_service.evaluate_writing_with_nova_micro(
    essay_text=user_essay,
    prompt=task_prompt,
    assessment_type='academic_task2'
)

# Returns:
# {
#     "overall_band": 7.5,
#     "criteria_scores": {...},
#     "detailed_feedback": {...},
#     "model_used": "amazon.nova-micro-v1:0"
# }
```

#### 4. `dynamodb_dal.py` - Database Access Layer

**Classes:**
- `DynamoDBConnection` - Handles boto3 client initialization
- `UserDAL` - User CRUD operations
- `SessionDAL` - Session management with TTL
- `AssessmentDAL` - Assessment history and results
- `QRTokenDAL` - QR code token validation

**Tables:**
- `ielts-genai-prep-users` - User accounts
- `ielts-genai-prep-sessions` - Active sessions with TTL
- `ielts-genai-prep-assessments` - Assessment results
- `ielts-genai-prep-qr-tokens` - QR authentication tokens
- `ielts-genai-prep-entitlements` - User purchase entitlements
- `ielts-assessment-questions` - Question bank
- `ielts-assessment-rubrics` - Assessment rubrics
- `ielts-ai-safety-logs` - AI safety monitoring
- `ielts-content-reports` - Content moderation reports

**Example:**
```python
db = DynamoDBConnection(environment='production')
user_dal = UserDAL(db)

# Create user
user_dal.create_user(
    user_id='user_123',
    email='test@example.com',
    password_hash='...'
)

# Query user
user = user_dal.get_user_by_email('test@example.com')
```

## AWS Infrastructure

### Lambda Function Configuration

**Function Name:** `ielts-ai-prep-production`

**Runtime Settings:**
- Runtime: Python 3.11
- Architecture: x86_64
- Memory: 512 MB (optimal for Flask + AI)
- Timeout: 30 seconds (API Gateway max)
- Handler: `lambda_handler.handler`

**Environment Variables:**
```bash
AWS_REGION=us-east-1
ENVIRONMENT=production
GOOGLE_CLOUD_PROJECT=your-gcp-project-id
GEMINI_API_KEY=your-vertex-ai-key
SESSION_SECRET=your-secure-random-secret
RECAPTCHA_V2_SITE_KEY=your-recaptcha-site-key
RECAPTCHA_V2_SECRET_KEY=your-recaptcha-secret
SENDGRID_API_KEY=your-sendgrid-key
```

**IAM Role Permissions:**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "dynamodb:GetItem",
        "dynamodb:PutItem",
        "dynamodb:UpdateItem",
        "dynamodb:Query",
        "dynamodb:Scan",
        "dynamodb:DeleteItem"
      ],
      "Resource": "arn:aws:dynamodb:*:*:table/ielts-*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel"
      ],
      "Resource": "arn:aws:bedrock:*::foundation-model/amazon.nova-micro-v1:0"
    },
    {
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws:logs:*:*:*"
    }
  ]
}
```

### DynamoDB Tables

#### ielts-genai-prep-users

**Primary Key:** `user_id` (String)

**Global Secondary Indexes:**
- `email-index`: Query by email for login

**Attributes:**
- `user_id`: Unique identifier (UUID)
- `email`: User email (unique)
- `password_hash`: bcrypt hashed password
- `verified`: Email verification status
- `subscription_tier`: free | writing | speaking | full
- `created_at`: ISO timestamp
- `updated_at`: ISO timestamp

**Capacity:** On-Demand (auto-scaling)

#### ielts-genai-prep-sessions

**Primary Key:** `session_id` (String)

**TTL Attribute:** `expires_at` (auto-cleanup after expiration)

**Attributes:**
- `session_id`: Session token
- `user_id`: Associated user
- `created_at`: Session start time
- `expires_at`: TTL expiration (24 hours)
- `last_accessed`: Last activity timestamp

#### ielts-genai-prep-assessments

**Primary Key:** `assessment_id` (String)

**Global Secondary Indexes:**
- `user_id-index`: Query user's assessment history

**Attributes:**
- `assessment_id`: Unique ID (UUID)
- `user_id`: User who took assessment
- `type`: speaking | writing | reading | listening
- `subtype`: academic | general_training
- `scores`: JSON object with band scores
- `feedback`: JSON object with AI feedback
- `ai_model`: Model used for evaluation
- `timestamp`: ISO timestamp
- `duration_seconds`: Time taken

#### ielts-genai-prep-qr-tokens

**Primary Key:** `token` (String)

**TTL Attribute:** `expires_at` (5 minutes)

**Attributes:**
- `token`: QR code token (secure random)
- `user_id`: Associated user
- `created_at`: Token generation time
- `expires_at`: TTL (5 minutes from creation)
- `used`: Boolean flag (prevents reuse)

### API Gateway Configuration

**API Name:** `ielts-api-production`

**Stage:** `prod`

**Custom Domain:** `api.ieltsaiprep.com` (via Route 53)

**CORS Configuration:**
```json
{
  "allowOrigins": ["https://ieltsaiprep.com", "https://www.ieltsaiprep.com"],
  "allowMethods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
  "allowHeaders": ["Content-Type", "Authorization", "X-Requested-With"],
  "maxAge": 3600
}
```

**Routes:**
- `ANY /` → Lambda function (all HTTP methods)
- `ANY /{proxy+}` → Lambda function (catch-all)

### CloudFront Distribution

**Origin:** API Gateway custom domain

**Behaviors:**
- `/static/*` → Cache for 1 year (max-age=31536000)
- `/api/*` → No cache, forward all headers
- `/*` → Cache for 5 minutes with query string forwarding

**Custom Headers (Security):**
```
X-Custom-Auth: {secret-value}  # Blocks direct API Gateway access
```

**SSL Certificate:** AWS Certificate Manager (ACM) for `*.ieltsaiprep.com`

### Route 53 DNS

**Hosted Zone:** `ieltsaiprep.com`

**Records:**
- `A ieltsaiprep.com` → CloudFront distribution (alias)
- `A www.ieltsaiprep.com` → CloudFront distribution (alias)
- `A api.ieltsaiprep.com` → API Gateway (alias)

## Deployment Process

### Prerequisites

1. AWS CLI configured with appropriate credentials
2. Python 3.11 installed locally
3. All environment variables set in AWS Lambda console or Systems Manager

### Step 1: Package Dependencies

```bash
# Navigate to deployment folder
cd deployment

# Install dependencies
pip install -r requirements.txt -t .

# Verify package size (must be < 250MB zipped, < 512MB unzipped)
du -sh .
```

### Step 2: Create Deployment Package

```bash
# Create ZIP file (from deployment folder)
zip -r ../ielts-ai-prep-lambda.zip . \
  -x "*.pyc" \
  -x "*__pycache__*" \
  -x "*.git*" \
  -x "*.DS_Store"

# Verify ZIP size
ls -lh ../ielts-ai-prep-lambda.zip
```

**Expected Size:** ~45-50 MB (well under 50MB zipped limit)

### Step 3: Upload to S3 (Recommended for >50MB)

```bash
# Create S3 bucket if not exists
aws s3 mb s3://ielts-lambda-deployments

# Upload package
aws s3 cp ../ielts-ai-prep-lambda.zip s3://ielts-lambda-deployments/ielts-ai-prep-lambda-$(date +%Y%m%d-%H%M%S).zip
```

### Step 4: Deploy Infrastructure (First Time)

```bash
# Deploy CloudFormation stack
aws cloudformation deploy \
  --template-file ../ielts-genai-prep-cloudformation.yaml \
  --stack-name ielts-ai-prep-production \
  --capabilities CAPABILITY_IAM \
  --parameter-overrides \
    Environment=production \
    GeminiAPIKey=$GEMINI_API_KEY \
    SessionSecret=$SESSION_SECRET
```

### Step 5: Update Lambda Code

```bash
# Update function code from S3
aws lambda update-function-code \
  --function-name ielts-ai-prep-production \
  --s3-bucket ielts-lambda-deployments \
  --s3-key ielts-ai-prep-lambda-20251012-120000.zip

# Or upload directly (for <50MB)
aws lambda update-function-code \
  --function-name ielts-ai-prep-production \
  --zip-file fileb://../ielts-ai-prep-lambda.zip
```

### Step 6: Verify Deployment

```bash
# Test Lambda function
aws lambda invoke \
  --function-name ielts-ai-prep-production \
  --payload '{"httpMethod":"GET","path":"/"}' \
  response.json

cat response.json
```

### Step 7: Monitor Deployment

```bash
# View CloudWatch logs
aws logs tail /aws/lambda/ielts-ai-prep-production --follow

# Check metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Invocations \
  --dimensions Name=FunctionName,Value=ielts-ai-prep-production \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 3600 \
  --statistics Sum
```

## Quick Deploy Script

For convenience, use the included deployment script:

```bash
#!/bin/bash
# File: deploy-to-aws-lambda.sh

set -e

echo "📦 Packaging Lambda deployment..."
cd deployment
pip install -r requirements.txt -t . --quiet
zip -rq ../ielts-ai-prep-lambda.zip .
cd ..

echo "☁️  Uploading to S3..."
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
aws s3 cp ielts-ai-prep-lambda.zip s3://ielts-lambda-deployments/ielts-ai-prep-lambda-$TIMESTAMP.zip

echo "🚀 Updating Lambda function..."
aws lambda update-function-code \
  --function-name ielts-ai-prep-production \
  --s3-bucket ielts-lambda-deployments \
  --s3-key ielts-ai-prep-lambda-$TIMESTAMP.zip

echo "✅ Deployment complete!"
echo "📊 View logs: aws logs tail /aws/lambda/ielts-ai-prep-production --follow"
```

Usage:
```bash
chmod +x deploy-to-aws-lambda.sh
./deploy-to-aws-lambda.sh
```

## Testing

### Local Testing

```bash
# Run Flask locally (uses mock services if AWS not configured)
cd deployment
python lambda_handler.py

# Access at http://localhost:5000
```

### Lambda Testing with SAM

```bash
# Install AWS SAM CLI
brew install aws-sam-cli  # macOS

# Test locally with SAM
sam local start-api -t ../ielts-genai-prep-cloudformation.yaml

# Access at http://localhost:3000
```

### Load Testing

```bash
# Install artillery
npm install -g artillery

# Run load test
artillery quick --count 100 --num 10 https://api.ieltsaiprep.com/

# Expected: 100 users, 10 requests each, <500ms p95 latency
```

## Monitoring & Debugging

### CloudWatch Logs

```bash
# Real-time logs
aws logs tail /aws/lambda/ielts-ai-prep-production --follow

# Search for errors
aws logs filter-log-events \
  --log-group-name /aws/lambda/ielts-ai-prep-production \
  --filter-pattern "ERROR"

# Get recent invocations
aws logs describe-log-streams \
  --log-group-name /aws/lambda/ielts-ai-prep-production \
  --order-by LastEventTime \
  --descending
```

### CloudWatch Metrics

**Key Metrics to Monitor:**
- `Invocations` - Total requests
- `Errors` - Failed invocations
- `Duration` - Execution time
- `ConcurrentExecutions` - Active instances
- `Throttles` - Rate-limited requests

**Alarms:**
- Error rate > 5% → SNS notification
- Duration > 25 seconds → Potential timeout
- Throttles > 0 → Need reserved concurrency

### X-Ray Tracing (Optional)

Enable AWS X-Ray for detailed request tracing:

```python
# Add to lambda_handler.py
from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.ext.flask.middleware import XRayMiddleware

xray_recorder.configure(service='ielts-ai-prep')
XRayMiddleware(app, xray_recorder)
```

## Cost Optimization

### Current Costs (Production)

**Lambda:**
- 5M requests/month × $0.20 per 1M = $1.00
- 5M × 1s × 512MB × $0.0000000083 = $24.00
- **Subtotal: $25/month**

**DynamoDB:**
- On-demand reads (1M/month) = $12.50
- On-demand writes (100K/month) = $2.50
- **Subtotal: $15/month**

**API Gateway:**
- 5M requests × $3.50 per 1M = $17.50

**CloudFront:**
- 10GB transfer × $0.085 = $0.85

**Total Infrastructure: ~$60/month**

### Optimization Strategies

1. **Reserved Concurrency:** $5.83/month per provisioned unit (for predictable traffic)
2. **DynamoDB Reserved Capacity:** 30% savings with 1-year commitment
3. **S3 Lifecycle Policies:** Move old logs to Glacier after 30 days
4. **Lambda Power Tuning:** Optimize memory allocation (current 512MB may be overkill)

## Troubleshooting

### Common Issues

#### Issue: "Module not found" error

**Solution:** Ensure all dependencies are in deployment package
```bash
cd deployment
pip install -r requirements.txt -t . --upgrade
```

#### Issue: Lambda timeout (30s)

**Solution:** Check CloudWatch logs for slow operations
```bash
aws logs filter-log-events \
  --log-group-name /aws/lambda/ielts-ai-prep-production \
  --filter-pattern "Task timed out"
```

#### Issue: DynamoDB "Provisioned throughput exceeded"

**Solution:** Switch to on-demand mode or increase provisioned capacity

#### Issue: Cold start latency >1s

**Solution:** Enable provisioned concurrency (min 1 instance)
```bash
aws lambda put-provisioned-concurrency-config \
  --function-name ielts-ai-prep-production \
  --provisioned-concurrent-executions 1
```

## Security Best Practices

1. **Environment Variables:** Store in AWS Systems Manager Parameter Store (encrypted)
2. **IAM Permissions:** Least privilege principle (only necessary permissions)
3. **API Gateway:** Enable request validation and throttling
4. **CloudFront:** Custom header verification to block direct API access
5. **DynamoDB:** Encryption at rest enabled by default
6. **Lambda:** Run in VPC for additional network isolation (optional)

## Backup & Disaster Recovery

### DynamoDB Backups

```bash
# Enable point-in-time recovery
aws dynamodb update-continuous-backups \
  --table-name ielts-users-production \
  --point-in-time-recovery-specification PointInTimeRecoveryEnabled=true

# Create on-demand backup
aws dynamodb create-backup \
  --table-name ielts-users-production \
  --backup-name ielts-users-backup-$(date +%Y%m%d)
```

### Lambda Version Management

```bash
# Publish new version
aws lambda publish-version \
  --function-name ielts-ai-prep-production \
  --description "Deployment $(date +%Y%m%d-%H%M%S)"

# Create alias
aws lambda create-alias \
  --function-name ielts-ai-prep-production \
  --name production \
  --function-version 5
```

## Summary

The `/deployment` folder is a complete, production-ready AWS Lambda package containing:
- ✅ Flask application with AWS integration
- ✅ All dependencies packaged
- ✅ DynamoDB data access layer
- ✅ AWS Bedrock service integration
- ✅ Gemini Smart Selection for speaking
- ✅ Complete frontend (templates + static files)

**Current Status:**
- 🟢 **Deployed:** AWS Lambda in production
- 🟢 **Database:** DynamoDB with 4 tables
- 🟢 **API:** API Gateway with custom domain
- 🟢 **CDN:** CloudFront distribution
- 🟢 **Cost:** ~$60/month infrastructure

**Next Steps:**
1. Push `/deployment` folder to GitHub
2. Document deployment process in CI/CD pipeline
3. Set up automated testing and deployment

---

**Last Updated:** October 12, 2025  
**Deployment Package Version:** 1.0.0  
**AWS Region:** us-east-1
