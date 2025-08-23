#!/bin/bash
# Build and push Docker container to Google Container Registry

set -e

PROJECT_ID="water-futures-ai"
IMAGE_NAME="gcr.io/water-futures-ai/nqh2o-predictor"
REGION="us-central1"

echo "Building Docker image..."
docker build -t $IMAGE_NAME .

echo "Pushing image to GCR..."
docker push $IMAGE_NAME

echo "✓ Container image ready: $IMAGE_NAME"
