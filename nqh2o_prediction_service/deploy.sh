#!/bin/bash
# Deploy model to Vertex AI

set -e

PROJECT_ID="water-futures-ai"
REGION="us-central1"
MODEL_NAME="nqh2o-forecasting"
ENDPOINT_NAME="nqh2o-prediction-endpoint"
IMAGE_URI="gcr.io/water-futures-ai/nqh2o-predictor"

echo "Uploading model to Vertex AI..."
gcloud ai models upload \
    --region=$REGION \
    --display-name=$MODEL_NAME \
    --container-image-uri=$IMAGE_URI \
    --container-health-route=/health \
    --container-predict-route=/predict \
    --container-ports=8080

echo "Creating endpoint..."
gcloud ai endpoints create \
    --region=$REGION \
    --display-name=$ENDPOINT_NAME

echo "Deploying model to endpoint..."
ENDPOINT_ID=$(gcloud ai endpoints list --region=$REGION --filter="displayName:$ENDPOINT_NAME" --format="value(name)" | head -1)
MODEL_ID=$(gcloud ai models list --region=$REGION --filter="displayName:$MODEL_NAME" --format="value(name)" | head -1)

gcloud ai endpoints deploy-model $ENDPOINT_ID \
    --region=$REGION \
    --model=$MODEL_ID \
    --display-name=$MODEL_NAME-deployment \
    --machine-type=n1-standard-2 \
    --min-replica-count=1 \
    --max-replica-count=3

echo "✓ Model deployed successfully!"
echo "Endpoint ID: $ENDPOINT_ID"
