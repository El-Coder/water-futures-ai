#!/bin/bash
# Deploy NQH2O model to Vertex AI using Cloud Build (no local Docker required)

set -e

PROJECT_ID="water-futures-ai"
REGION="us-central1"
MODEL_NAME="nqh2o-forecasting"
ENDPOINT_NAME="nqh2o-prediction-endpoint"
IMAGE_NAME="nqh2o-predictor"
IMAGE_URI="gcr.io/${PROJECT_ID}/${IMAGE_NAME}"

echo "=== NQH2O Model Deployment to Vertex AI ==="
echo "Project: ${PROJECT_ID}"
echo "Region: ${REGION}"
echo ""

# Step 1: Build and push container using Cloud Build
echo "Step 1: Building and pushing Docker container using Cloud Build..."
gcloud builds submit . \
    --tag ${IMAGE_URI} \
    --project ${PROJECT_ID} \
    --timeout=20m

if [ $? -eq 0 ]; then
    echo "✓ Container successfully built and pushed to ${IMAGE_URI}"
else
    echo "✗ Failed to build container. Please check the logs above."
    exit 1
fi

# Step 2: Upload model to Vertex AI
echo ""
echo "Step 2: Uploading model to Vertex AI..."
MODEL_UPLOAD_OUTPUT=$(gcloud ai models upload \
    --region=${REGION} \
    --display-name=${MODEL_NAME} \
    --container-image-uri=${IMAGE_URI} \
    --container-health-route=/health \
    --container-predict-route=/predict \
    --container-ports=8080 \
    --project=${PROJECT_ID} \
    --format="value(name)" 2>&1)

if [ $? -eq 0 ]; then
    MODEL_ID=$(echo ${MODEL_UPLOAD_OUTPUT} | grep -oE '[0-9]+$')
    echo "✓ Model uploaded successfully. Model ID: ${MODEL_ID}"
else
    echo "Model might already exist. Checking existing models..."
    MODEL_ID=$(gcloud ai models list \
        --region=${REGION} \
        --filter="displayName:${MODEL_NAME}" \
        --format="value(name)" \
        --project=${PROJECT_ID} | head -1 | grep -oE '[0-9]+$')
    
    if [ -z "${MODEL_ID}" ]; then
        echo "✗ Failed to upload model and no existing model found."
        exit 1
    fi
    echo "✓ Using existing model. Model ID: ${MODEL_ID}"
fi

# Step 3: Create or get endpoint
echo ""
echo "Step 3: Creating or getting endpoint..."
ENDPOINT_ID=$(gcloud ai endpoints list \
    --region=${REGION} \
    --filter="displayName:${ENDPOINT_NAME}" \
    --format="value(name)" \
    --project=${PROJECT_ID} | head -1 | grep -oE '[0-9]+$')

if [ -z "${ENDPOINT_ID}" ]; then
    echo "Creating new endpoint..."
    ENDPOINT_CREATE_OUTPUT=$(gcloud ai endpoints create \
        --region=${REGION} \
        --display-name=${ENDPOINT_NAME} \
        --project=${PROJECT_ID} \
        --format="value(name)" 2>&1)
    
    if [ $? -eq 0 ]; then
        ENDPOINT_ID=$(echo ${ENDPOINT_CREATE_OUTPUT} | grep -oE '[0-9]+$')
        echo "✓ Endpoint created successfully. Endpoint ID: ${ENDPOINT_ID}"
    else
        echo "✗ Failed to create endpoint."
        exit 1
    fi
else
    echo "✓ Using existing endpoint. Endpoint ID: ${ENDPOINT_ID}"
fi

# Step 4: Deploy model to endpoint
echo ""
echo "Step 4: Deploying model to endpoint..."
echo "This may take 5-10 minutes..."

# Check if model is already deployed
DEPLOYED_MODELS=$(gcloud ai endpoints describe ${ENDPOINT_ID} \
    --region=${REGION} \
    --project=${PROJECT_ID} \
    --format="value(deployedModels[].model)" 2>/dev/null | grep -E "${MODEL_ID}$" || true)

if [ -n "${DEPLOYED_MODELS}" ]; then
    echo "✓ Model is already deployed to this endpoint."
else
    gcloud ai endpoints deploy-model ${ENDPOINT_ID} \
        --region=${REGION} \
        --model=${MODEL_ID} \
        --display-name=${MODEL_NAME}-deployment \
        --machine-type=n1-standard-2 \
        --min-replica-count=1 \
        --max-replica-count=3 \
        --project=${PROJECT_ID}
    
    if [ $? -eq 0 ]; then
        echo "✓ Model deployed successfully!"
    else
        echo "✗ Failed to deploy model to endpoint."
        exit 1
    fi
fi

# Step 5: Display deployment information
echo ""
echo "=== Deployment Complete ==="
echo "Project ID: ${PROJECT_ID}"
echo "Region: ${REGION}"
echo "Model ID: ${MODEL_ID}"
echo "Endpoint ID: ${ENDPOINT_ID}"
echo "Container Image: ${IMAGE_URI}"
echo ""
echo "Endpoint URL: https://${REGION}-aiplatform.googleapis.com/v1/projects/${PROJECT_ID}/locations/${REGION}/endpoints/${ENDPOINT_ID}:predict"
echo ""
echo "To test your deployment, update client_example.py with:"
echo "  PROJECT_ID = \"${PROJECT_ID}\""
echo "  REGION = \"${REGION}\""
echo "  ENDPOINT_ID = \"${ENDPOINT_ID}\""
echo ""
echo "Then run: python client_example.py"