#!/bin/bash

# Deploy script for Water Futures AI to Google Cloud Run

set -e

PROJECT_ID="water-futures-ai"
REGION="us-central1"

echo "🚀 Starting deployment to Google Cloud Run..."

# Set the project
gcloud config set project $PROJECT_ID

# Enable required APIs
echo "📦 Enabling required APIs..."
gcloud services enable \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  containerregistry.googleapis.com \
  artifactregistry.googleapis.com

# Build and deploy backend
echo "🔨 Building backend Docker image..."
cd backend
gcloud builds submit --tag gcr.io/$PROJECT_ID/water-futures-backend

echo "🚀 Deploying backend to Cloud Run..."
gcloud run deploy water-futures-backend \
  --image gcr.io/$PROJECT_ID/water-futures-backend \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --port 8000 \
  --memory 1Gi \
  --cpu 1 \
  --set-env-vars "GCP_PROJECT_ID=$PROJECT_ID,ANTHROPIC_API_KEY=your_anthropic_api_key_here"

# Get backend URL
BACKEND_URL=$(gcloud run services describe water-futures-backend \
  --platform managed \
  --region $REGION \
  --format 'value(status.url)')

echo "✅ Backend deployed at: $BACKEND_URL"

# Build and deploy frontend
echo "🔨 Building frontend Docker image..."
cd ../frontend

# Update the API URL in the frontend build
echo "VITE_API_URL=$BACKEND_URL" > .env.production

gcloud builds submit --tag gcr.io/$PROJECT_ID/water-futures-frontend

echo "🚀 Deploying frontend to Cloud Run..."
gcloud run deploy water-futures-frontend \
  --image gcr.io/$PROJECT_ID/water-futures-frontend \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --port 80 \
  --memory 512Mi \
  --cpu 1

# Get frontend URL
FRONTEND_URL=$(gcloud run services describe water-futures-frontend \
  --platform managed \
  --region $REGION \
  --format 'value(status.url)')

echo "✅ Frontend deployed at: $FRONTEND_URL"

echo "
🎉 Deployment complete!

Frontend: $FRONTEND_URL
Backend API: $BACKEND_URL

To view logs:
gcloud logs read --service water-futures-backend
gcloud logs read --service water-futures-frontend
"