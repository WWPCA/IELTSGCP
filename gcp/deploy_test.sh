#!/bin/bash
# Quick Deployment Script for test.ieltsaiprep.com
# Preview environment for UI/pricing testing

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Test Environment Deployment${NC}"
echo -e "${GREEN}test.ieltsaiprep.com${NC}"
echo -e "${GREEN}========================================${NC}"

PROJECT_ID=${GOOGLE_CLOUD_PROJECT:-""}

if [ -z "$PROJECT_ID" ]; then
    echo -e "${YELLOW}Error: GOOGLE_CLOUD_PROJECT not set${NC}"
    exit 1
fi

echo -e "${YELLOW}Deploying to: ${PROJECT_ID}${NC}"

# Step 1: Copy current app.py to Cloud Run directory
echo -e "${GREEN}Step 1: Preparing application code...${NC}"
cp ../app.py cloud_run/app_full.py
cp -r ../templates cloud_run/ 2>/dev/null || echo "Templates already copied"
cp -r ../static cloud_run/ 2>/dev/null || echo "Static files already copied"

# Step 2: Build test image
echo -e "${GREEN}Step 2: Building container image...${NC}"
cd cloud_run
gcloud builds submit \
    --tag us-central1-docker.pkg.dev/${PROJECT_ID}/ielts-genai-prep/app:test \
    --project=$PROJECT_ID

cd ..

# Step 3: Deploy test infrastructure
echo -e "${GREEN}Step 3: Deploying test infrastructure...${NC}"
cd terraform

terraform init
terraform apply \
    -var="project_id=${PROJECT_ID}" \
    -target=google_cloud_run_v2_service.test_app \
    -target=google_dns_record_set.test_subdomain \
    -target=google_compute_global_address.test_ip \
    -target=google_compute_backend_service.test \
    -auto-approve

cd ..

# Get test URL
TEST_URL=$(gcloud run services describe ielts-genai-prep-test \
    --region=us-central1 \
    --project=$PROJECT_ID \
    --format="value(status.url)")

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Test Deployment Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${YELLOW}Direct Cloud Run URL:${NC} $TEST_URL"
echo -e "${YELLOW}Custom Domain:${NC} https://test.ieltsaiprep.com"
echo ""
echo -e "${YELLOW}Note:${NC} SSL certificate for test.ieltsaiprep.com will take 15-30 minutes to provision"
echo -e "${YELLOW}Use the Cloud Run URL immediately, or wait for DNS + SSL${NC}"
echo ""
