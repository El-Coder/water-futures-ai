#!/bin/bash

# Deploy Water Futures AI to Google Cloud Run
# Usage: ./deploy.sh [project-id]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ID=${1:-water-futures-ai}
REGION=us-central1
BACKEND_SERVICE=water-futures-backend
MCP_SERVICE=water-futures-mcp

echo -e "${BLUE}======================================${NC}"
echo -e "${BLUE}Water Futures AI - Cloud Run Deployment${NC}"
echo -e "${BLUE}======================================${NC}"
echo -e "${YELLOW}Project ID: ${PROJECT_ID}${NC}"
echo -e "${YELLOW}Region: ${REGION}${NC}"
echo ""

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}Error: gcloud CLI is not installed${NC}"
    echo "Please install: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Set project
echo -e "${YELLOW}Setting project...${NC}"
gcloud config set project ${PROJECT_ID}

# Enable required APIs
echo -e "${YELLOW}Enabling required APIs...${NC}"
gcloud services enable run.googleapis.com \
    containerregistry.googleapis.com \
    cloudbuild.googleapis.com

# Configure Docker
echo -e "${YELLOW}Configuring Docker...${NC}"
gcloud auth configure-docker

# Build and deploy backend
echo -e "${GREEN}Building and deploying backend...${NC}"
cd backend

# Build Docker image
docker build -t gcr.io/${PROJECT_ID}/${BACKEND_SERVICE} .

# Push to Container Registry
docker push gcr.io/${PROJECT_ID}/${BACKEND_SERVICE}

# Deploy to Cloud Run
gcloud run deploy ${BACKEND_SERVICE} \
    --image gcr.io/${PROJECT_ID}/${BACKEND_SERVICE} \
    --region ${REGION} \
    --platform managed \
    --allow-unauthenticated \
    --memory 2Gi \
    --cpu 2 \
    --max-instances 10 \
    --min-instances 1 \
    --port 8080

# Get backend URL
BACKEND_URL=$(gcloud run services describe ${BACKEND_SERVICE} --region ${REGION} --format 'value(status.url)')
echo -e "${GREEN}Backend deployed at: ${BACKEND_URL}${NC}"

cd ..

# Build and deploy MCP servers
echo -e "${GREEN}Building and deploying MCP servers...${NC}"
cd mcp-servers

# Create package-lock.json if it doesn't exist
if [ ! -f package-lock.json ]; then
    npm install
fi

# Build Docker image
docker build -t gcr.io/${PROJECT_ID}/${MCP_SERVICE} .

# Push to Container Registry
docker push gcr.io/${PROJECT_ID}/${MCP_SERVICE}

# Deploy to Cloud Run with backend URL
gcloud run deploy ${MCP_SERVICE} \
    --image gcr.io/${PROJECT_ID}/${MCP_SERVICE} \
    --region ${REGION} \
    --platform managed \
    --allow-unauthenticated \
    --memory 1Gi \
    --cpu 1 \
    --max-instances 10 \
    --min-instances 1 \
    --port 8080 \
    --set-env-vars "BACKEND_URL=${BACKEND_URL}"

# Get MCP URL
MCP_URL=$(gcloud run services describe ${MCP_SERVICE} --region ${REGION} --format 'value(status.url)')
echo -e "${GREEN}MCP Server deployed at: ${MCP_URL}${NC}"

cd ..

# Update frontend with service URLs
echo -e "${YELLOW}Updating frontend configuration...${NC}"
cat > frontend/.env.production << EOF
REACT_APP_API_URL=${BACKEND_URL}
REACT_APP_MCP_URL=${MCP_URL}
EOF

echo -e "${GREEN}======================================${NC}"
echo -e "${GREEN}Deployment Complete!${NC}"
echo -e "${GREEN}======================================${NC}"
echo ""
echo -e "${BLUE}Service URLs:${NC}"
echo -e "Backend API: ${BACKEND_URL}"
echo -e "MCP Server: ${MCP_URL}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Add secrets to Cloud Run services:"
echo "   gcloud run services update ${BACKEND_SERVICE} --region ${REGION} --update-env-vars KEY=VALUE"
echo "2. Deploy frontend to Firebase Hosting"
echo "3. Configure custom domain (optional)"
echo ""
echo -e "${GREEN}Happy trading! 🚀${NC}"