#!/bin/bash

# IELTS AI Prep - AWS Lambda Deployment Script
# Deploys Flask application to existing Lambda infrastructure

set -e

echo "🚀 IELTS AI Prep - AWS Lambda Deployment"
echo "========================================="

# Configuration
AWS_REGION="${AWS_REGION:-us-east-1}"
LAMBDA_FUNCTION_NAME="ielts-genai-prep-api"
DEPLOYMENT_PACKAGE="ielts-ai-prep-lambda.zip"
CLOUDFRONT_DISTRIBUTION_ID="E1EPXAU67877FR"

echo "📋 Configuration:"
echo "   Region: $AWS_REGION"
echo "   Lambda Function: $LAMBDA_FUNCTION_NAME"
echo "   CloudFront ID: $CLOUDFRONT_DISTRIBUTION_ID"
echo ""

# Step 1: Create deployment directory
echo "📦 Step 1: Creating deployment package..."
rm -rf deployment/
mkdir -p deployment/

# Copy application files
echo "   Copying application files..."
cp app.py deployment/
cp lambda_handler.py deployment/
cp dynamodb_dal.py deployment/
cp bedrock_service.py deployment/
cp -r templates deployment/ 2>/dev/null || echo "   No templates directory"
cp -r static deployment/ 2>/dev/null || echo "   No static directory"

# Create requirements.txt for Lambda (minimal - boto3 already in Lambda)
cat > deployment/requirements.txt << 'EOF'
aws-wsgi
flask
werkzeug
flask-cors
flask-login
pyjwt
bcrypt
qrcode
EOF

# Step 2: Install dependencies
echo ""
echo "📚 Step 2: Installing dependencies..."
cd deployment/

# Install Python packages (force no user mode)
pip install -r requirements.txt -t . --upgrade --quiet --no-user 2>/dev/null || \
python -m pip install -r requirements.txt -t . --upgrade --quiet --no-user 2>/dev/null || \
pip3 install -r requirements.txt -t . --upgrade --quiet --no-user

echo "   Dependencies installed"

# Step 3: Create deployment package
echo ""
echo "📦 Step 3: Creating deployment ZIP..."
# Create ZIP from within deployment directory so files are at root level
zip -r ../$DEPLOYMENT_PACKAGE . -q -x "*.pyc" "*__pycache__*" "*.git*"
cd ..

PACKAGE_SIZE=$(du -h $DEPLOYMENT_PACKAGE | cut -f1)
echo "   Package size: $PACKAGE_SIZE"

# Step 4: Upload to S3 first (package too large for direct upload)
echo ""
echo "📤 Step 4: Uploading to S3..."
S3_BUCKET="ielts-genai-prep-deployments-116981806044"
S3_KEY="lambda/${LAMBDA_FUNCTION_NAME}-$(date +%Y%m%d-%H%M%S).zip"

# Upload to S3
aws s3 cp $DEPLOYMENT_PACKAGE s3://$S3_BUCKET/$S3_KEY --region $AWS_REGION
echo "   Uploaded to s3://$S3_BUCKET/$S3_KEY"

# Step 5: Update Lambda from S3
echo ""
echo "🚀 Step 5: Deploying to AWS Lambda from S3..."
aws lambda update-function-code \
    --function-name $LAMBDA_FUNCTION_NAME \
    --s3-bucket $S3_BUCKET \
    --s3-key $S3_KEY \
    --region $AWS_REGION \
    --output json > /tmp/lambda-update-result.json

if [ $? -eq 0 ]; then
    echo "✅ Lambda function updated successfully!"
else
    echo "❌ Failed to update Lambda function"
    exit 1
fi

# Step 6: Wait for Lambda to be ready
echo ""
echo "⏳ Step 6: Waiting for Lambda to be ready..."
sleep 5

# Update environment variables (skip AWS_REGION as it's reserved)
echo ""
echo "🔧 Step 7: Updating Lambda environment variables..."
aws lambda update-function-configuration \
    --function-name $LAMBDA_FUNCTION_NAME \
    --environment "Variables={
        ENVIRONMENT=production,
        SESSION_SECRET=${SESSION_SECRET:-$(openssl rand -hex 32)}
    }" \
    --region $AWS_REGION \
    --output json > /dev/null 2>&1

echo "   Environment variables updated"

# Step 8: Invalidate CloudFront cache
echo ""
echo "🔄 Step 8: Invalidating CloudFront cache..."
INVALIDATION_OUTPUT=$(aws cloudfront create-invalidation \
    --distribution-id $CLOUDFRONT_DISTRIBUTION_ID \
    --paths "/*" \
    --output json)

INVALIDATION_ID=$(echo $INVALIDATION_OUTPUT | jq -r '.Invalidation.Id')
echo "   Invalidation ID: $INVALIDATION_ID"
echo "   Status: In Progress (will complete in 1-2 minutes)"

# Clean up
echo ""
echo "🧹 Cleaning up..."
rm -rf deployment/
# Keep the ZIP file for backup
# rm -f $DEPLOYMENT_PACKAGE

echo ""
echo "✅ Deployment Complete!"
echo ""
echo "📋 Next Steps:"
echo "   1. Wait for CloudFront invalidation to complete (~2 minutes)"
echo "   2. Test the deployment: curl https://www.ieltsaiprep.com/health"
echo "   3. Monitor logs: aws logs tail /aws/lambda/$LAMBDA_FUNCTION_NAME --follow"
echo ""
echo "🌐 Your application is live at:"
echo "   https://www.ieltsaiprep.com"
echo ""
