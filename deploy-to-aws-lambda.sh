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

# Create requirements.txt for Lambda
cat > deployment/requirements.txt << 'EOF'
boto3>=1.28.0
bcrypt>=4.0.0
qrcode>=7.4.0
Pillow>=10.0.0
flask>=2.3.0
flask-cors>=4.0.0
requests>=2.31.0
flask-login
pyjwt
mangum
werkzeug
EOF

# Step 2: Install dependencies
echo ""
echo "📚 Step 2: Installing dependencies..."
cd deployment/

# Install Python packages
pip install -r requirements.txt -t . --upgrade --quiet

echo "   Dependencies installed"

# Step 3: Create deployment package
echo ""
echo "📦 Step 3: Creating deployment ZIP..."
cd ..
zip -r $DEPLOYMENT_PACKAGE deployment/ -q -x "*.pyc" "*__pycache__*" "*.git*"

PACKAGE_SIZE=$(du -h $DEPLOYMENT_PACKAGE | cut -f1)
echo "   Package size: $PACKAGE_SIZE"

# Step 4: Upload to Lambda
echo ""
echo "🚀 Step 4: Deploying to AWS Lambda..."
aws lambda update-function-code \
    --function-name $LAMBDA_FUNCTION_NAME \
    --zip-file fileb://$DEPLOYMENT_PACKAGE \
    --region $AWS_REGION \
    --output json > /tmp/lambda-update-result.json

if [ $? -eq 0 ]; then
    echo "✅ Lambda function updated successfully!"
    echo "   Function ARN: $(jq -r '.FunctionArn' /tmp/lambda-update-result.json)"
    echo "   Last Modified: $(jq -r '.LastModified' /tmp/lambda-update-result.json)"
else
    echo "❌ Failed to update Lambda function"
    exit 1
fi

# Step 5: Wait for Lambda to be ready
echo ""
echo "⏳ Step 5: Waiting for Lambda to be ready..."
sleep 5

# Update environment variables
echo ""
echo "🔧 Step 6: Updating Lambda environment variables..."
aws lambda update-function-configuration \
    --function-name $LAMBDA_FUNCTION_NAME \
    --environment "Variables={
        AWS_REGION=$AWS_REGION,
        ENVIRONMENT=production,
        SESSION_SECRET=${SESSION_SECRET:-$(openssl rand -hex 32)}
    }" \
    --region $AWS_REGION \
    --output json > /dev/null

echo "   Environment variables updated"

# Step 7: Invalidate CloudFront cache
echo ""
echo "🔄 Step 7: Invalidating CloudFront cache..."
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
