#!/bin/bash

# Setup Google Cloud Project for Water Futures AI
# This script sets up all necessary GCP resources

set -e

PROJECT_ID=${1:-water-futures-ai}
REGION=us-central1
SERVICE_ACCOUNT_NAME=github-actions

echo "🚀 Setting up GCP Project: $PROJECT_ID"

# Set the project
gcloud config set project $PROJECT_ID

# Enable necessary APIs
echo "📦 Enabling required APIs..."
gcloud services enable \
  run.googleapis.com \
  artifactregistry.googleapis.com \
  cloudbuild.googleapis.com \
  secretmanager.googleapis.com \
  cloudresourcemanager.googleapis.com

# Create Artifact Registry repository
echo "🏗️ Creating Artifact Registry repository..."
gcloud artifacts repositories create water-futures \
  --repository-format=docker \
  --location=$REGION \
  --description="Water Futures AI Docker images" \
  || echo "Repository already exists"

# Create service account for GitHub Actions
echo "👤 Creating service account..."
gcloud iam service-accounts create $SERVICE_ACCOUNT_NAME \
  --display-name="GitHub Actions Deploy" \
  || echo "Service account already exists"

# Grant necessary permissions
echo "🔐 Granting permissions..."
SERVICE_ACCOUNT_EMAIL="$SERVICE_ACCOUNT_NAME@$PROJECT_ID.iam.gserviceaccount.com"

# Cloud Run permissions
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SERVICE_ACCOUNT_EMAIL" \
  --role="roles/run.admin"

# Artifact Registry permissions
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SERVICE_ACCOUNT_EMAIL" \
  --role="roles/artifactregistry.admin"

# Service Account User permission (to act as service account)
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SERVICE_ACCOUNT_EMAIL" \
  --role="roles/iam.serviceAccountUser"

# Cloud Build permissions (if using Cloud Build)
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SERVICE_ACCOUNT_EMAIL" \
  --role="roles/cloudbuild.builds.editor"

# Create service account key
echo "🔑 Creating service account key..."
gcloud iam service-accounts keys create github-key.json \
  --iam-account=$SERVICE_ACCOUNT_EMAIL

echo ""
echo "✅ Setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Add the following secrets to your GitHub repository:"
echo "   - GCP_SA_KEY: Contents of github-key.json"
echo "   - ANTHROPIC_API_KEY: Your Anthropic API key"
echo "   - ALPACA_API_KEY: Your Alpaca API key" 
echo "   - ALPACA_SECRET_KEY: Your Alpaca secret key"
echo "   - CROSSMINT_API_KEY: Your Crossmint API key"
echo "   - UNCLE_SAM_WALLET_ADDRESS: Government wallet address"
echo ""
echo "2. Delete the local key file after adding to GitHub:"
echo "   rm github-key.json"
echo ""
echo "3. Push your code to trigger deployment:"
echo "   git push origin main"