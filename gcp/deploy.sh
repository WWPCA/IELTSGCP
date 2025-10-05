#!/bin/bash
# GCP Deployment Script for IELTS GenAI Prep
# Multi-region deployment to us-central1, europe-west1, asia-southeast1

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ID=${GOOGLE_CLOUD_PROJECT:-""}
PRIMARY_REGION="us-central1"
SECONDARY_REGIONS="europe-west1 asia-southeast1"
ALL_REGIONS="${PRIMARY_REGION} ${SECONDARY_REGIONS}"

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}IELTS GenAI Prep - GCP Deployment${NC}"
echo -e "${GREEN}========================================${NC}"

# Check if project ID is set
if [ -z "$PROJECT_ID" ]; then
    echo -e "${RED}Error: GOOGLE_CLOUD_PROJECT environment variable not set${NC}"
    echo "Usage: export GOOGLE_CLOUD_PROJECT=your-project-id"
    exit 1
fi

echo -e "${YELLOW}Project ID: ${PROJECT_ID}${NC}"
echo -e "${YELLOW}Regions: ${ALL_REGIONS}${NC}"
echo ""

# Step 1: Enable required APIs
echo -e "${GREEN}Step 1: Enabling required APIs...${NC}"
gcloud services enable \
    run.googleapis.com \
    cloudfunctions.googleapis.com \
    firestore.googleapis.com \
    secretmanager.googleapis.com \
    cloudbuild.googleapis.com \
    artifactregistry.googleapis.com \
    dns.googleapis.com \
    cloudscheduler.googleapis.com \
    aiplatform.googleapis.com \
    language.googleapis.com \
    --project=$PROJECT_ID

# Step 2: Create Artifact Registry
echo -e "${GREEN}Step 2: Creating Artifact Registry...${NC}"
gcloud artifacts repositories create ielts-genai-prep \
    --repository-format=docker \
    --location=$PRIMARY_REGION \
    --description="Container images for IELTS GenAI Prep" \
    --project=$PROJECT_ID || echo "Repository already exists"

# Step 3: Build and push container image
echo -e "${GREEN}Step 3: Building and pushing container image...${NC}"
cd cloud_run
gcloud builds submit \
    --tag ${PRIMARY_REGION}-docker.pkg.dev/${PROJECT_ID}/ielts-genai-prep/app:latest \
    --project=$PROJECT_ID

cd ..

# Step 4: Deploy Terraform infrastructure
echo -e "${GREEN}Step 4: Deploying Terraform infrastructure...${NC}"
cd terraform

# Initialize Terraform
terraform init

# Plan
terraform plan \
    -var="project_id=${PROJECT_ID}" \
    -out=tfplan

# Apply
echo -e "${YELLOW}Review the plan above. Press Enter to continue or Ctrl+C to abort...${NC}"
read

terraform apply tfplan

cd ..

# Step 5: Add secrets to Secret Manager
echo -e "${GREEN}Step 5: Adding secrets to Secret Manager...${NC}"
echo -e "${YELLOW}Please add the following secrets manually:${NC}"
echo ""
echo "1. session-secret (random 32-byte string)"
echo "2. recaptcha-v2-secret-key (from Google reCAPTCHA)"
echo "3. apple-shared-secret (from App Store Connect)"
echo "4. google-service-account (Google Play service account JSON)"
echo "5. jwt-secret (random 32-byte string)"
echo "6. qr-encryption-key (random 32-byte string)"
echo "7. sendgrid-api-key (from SendGrid)"
echo ""
echo "Use: echo -n 'your-secret-value' | gcloud secrets versions add SECRET_NAME --data-file=-"
echo ""
echo -e "${YELLOW}Press Enter when secrets are added...${NC}"
read

# Step 6: Deploy Cloud Functions
echo -e "${GREEN}Step 6: Deploying Cloud Functions...${NC}"

# Package receipt validation function
cd cloud_functions/receipt_validation
zip -r ../../receipt_validation.zip .
cd ../..

# Package QR code handler function
cd cloud_functions/qr_code_handler
zip -r ../../qr_code_handler.zip .
cd ../..

# Upload to Cloud Storage
gsutil mb -p $PROJECT_ID -l $PRIMARY_REGION gs://${PROJECT_ID}-cloud-functions-source || echo "Bucket exists"
gsutil cp receipt_validation.zip gs://${PROJECT_ID}-cloud-functions-source/
gsutil cp qr_code_handler.zip gs://${PROJECT_ID}-cloud-functions-source/

# Deploy functions via Terraform (already done in Step 4)
echo "Cloud Functions deployed via Terraform"

# Step 7: Update DNS nameservers
echo -e "${GREEN}Step 7: DNS Migration${NC}"
echo -e "${YELLOW}Update your domain registrar with these Cloud DNS nameservers:${NC}"
terraform -chdir=terraform output dns_nameservers
echo ""
echo -e "${YELLOW}After updating nameservers, wait 24-48 hours for DNS propagation${NC}"

# Step 8: Verify deployment
echo -e "${GREEN}Step 8: Verifying deployment...${NC}"

# Get load balancer IP
LB_IP=$(terraform -chdir=terraform output -raw load_balancer_ip)
echo -e "Load Balancer IP: ${GREEN}${LB_IP}${NC}"

# Get Cloud Run URLs
echo -e "${YELLOW}Cloud Run services:${NC}"
for region in $ALL_REGIONS; do
    URL=$(gcloud run services describe ielts-genai-prep \
        --region=$region \
        --project=$PROJECT_ID \
        --format="value(status.url)")
    echo "  ${region}: ${URL}"
done

# Cleanup
rm -f receipt_validation.zip qr_code_handler.zip

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Deployment Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Update DNS nameservers at your domain registrar"
echo "2. Wait for SSL certificate provisioning (~15 minutes)"
echo "3. Test the application at https://www.ieltsaiprep.com"
echo "4. Monitor Cloud Run logs and metrics"
echo ""
echo -e "${YELLOW}Useful commands:${NC}"
echo "  gcloud run services list --project=${PROJECT_ID}"
echo "  gcloud logging tail 'resource.type=cloud_run_revision' --project=${PROJECT_ID}"
echo "  terraform -chdir=terraform destroy (to teardown)"
