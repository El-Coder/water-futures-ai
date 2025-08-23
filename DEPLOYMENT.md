# Water Futures AI - Deployment Guide

## 🚀 Cloud Run Deployment

This guide covers deploying the Water Futures AI platform to Google Cloud Run.

## Prerequisites

1. **Google Cloud Account** with billing enabled
2. **gcloud CLI** installed ([Install Guide](https://cloud.google.com/sdk/docs/install))
3. **Docker** installed locally
4. **Node.js 18+** and **Python 3.10+**

## Quick Deploy

### 1. One-Command Deployment

```bash
# Clone the repository
git clone https://github.com/your-org/water-futures-ai.git
cd water-futures-ai

# Run deployment script
./deploy.sh water-futures-ai
```

### 2. Manual Deployment

#### Deploy Backend

```bash
cd backend

# Build and push Docker image
docker build -t gcr.io/water-futures-ai/water-futures-backend .
docker push gcr.io/water-futures-ai/water-futures-backend

# Deploy to Cloud Run
gcloud run deploy water-futures-backend \
  --image gcr.io/water-futures-ai/water-futures-backend \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --port 8080
```

#### Deploy MCP Servers

```bash
cd mcp-servers

# Install dependencies
npm install

# Build and push Docker image
docker build -t gcr.io/water-futures-ai/water-futures-mcp .
docker push gcr.io/water-futures-ai/water-futures-mcp

# Deploy to Cloud Run
gcloud run deploy water-futures-mcp \
  --image gcr.io/water-futures-ai/water-futures-mcp \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated \
  --memory 1Gi \
  --cpu 1 \
  --port 8080
```

## Environment Variables

### Backend Service
```bash
gcloud run services update water-futures-backend \
  --region us-central1 \
  --update-env-vars \
    ANTHROPIC_API_KEY=your-key,\
    ALPACA_API_KEY=your-key,\
    ALPACA_SECRET_KEY=your-secret,\
    CROSSMINT_API_KEY=your-key,\
    UNCLE_SAM_WALLET_ADDRESS=your-address
```

### MCP Service
```bash
gcloud run services update water-futures-mcp \
  --region us-central1 \
  --update-env-vars \
    ANTHROPIC_API_KEY=your-key,\
    ALPACA_API_KEY=your-key,\
    ALPACA_SECRET_KEY=your-secret,\
    CROSSMINT_API_KEY=your-key,\
    BACKEND_URL=https://water-futures-backend-xxxxx.run.app
```

## CI/CD with GitHub Actions

### 1. Setup Service Account

```bash
# Create service account
gcloud iam service-accounts create github-actions \
  --display-name "GitHub Actions"

# Grant permissions
gcloud projects add-iam-policy-binding water-futures-ai \
  --member="serviceAccount:github-actions@water-futures-ai.iam.gserviceaccount.com" \
  --role="roles/run.admin"

gcloud projects add-iam-policy-binding water-futures-ai \
  --member="serviceAccount:github-actions@water-futures-ai.iam.gserviceaccount.com" \
  --role="roles/storage.admin"

# Create and download key
gcloud iam service-accounts keys create key.json \
  --iam-account=github-actions@water-futures-ai.iam.gserviceaccount.com
```

### 2. Add GitHub Secrets

Add these secrets to your GitHub repository:

- `GCP_SA_KEY`: Contents of `key.json`
- `ANTHROPIC_API_KEY`: Your Anthropic API key
- `ALPACA_API_KEY`: Your Alpaca API key
- `ALPACA_SECRET_KEY`: Your Alpaca secret key
- `CROSSMINT_API_KEY`: Your Crossmint API key
- `UNCLE_SAM_WALLET_ADDRESS`: Government wallet address

### 3. Deploy on Push

The GitHub Action will automatically deploy when you push to the `main` branch.

## Using Cloud Build

```bash
# Submit build using cloudbuild.yaml
gcloud builds submit --config cloudbuild.yaml
```

## Service URLs

After deployment, you'll get URLs like:

- **Backend**: `https://water-futures-backend-xxxxx-uc.a.run.app`
- **MCP Server**: `https://water-futures-mcp-xxxxx-uc.a.run.app`

## Frontend Deployment

### Update Frontend Configuration

```bash
# Update frontend/.env.production
REACT_APP_API_URL=https://water-futures-backend-xxxxx-uc.a.run.app
REACT_APP_MCP_URL=https://water-futures-mcp-xxxxx-uc.a.run.app
```

### Deploy to Firebase Hosting

```bash
cd frontend
npm run build
firebase deploy --only hosting
```

## Monitoring

### View Logs

```bash
# Backend logs
gcloud run services logs read water-futures-backend \
  --region us-central1

# MCP logs
gcloud run services logs read water-futures-mcp \
  --region us-central1
```

### Metrics

View metrics in the [Cloud Console](https://console.cloud.google.com/run).

## Scaling Configuration

### Backend (High Traffic)
- Min instances: 1
- Max instances: 10
- CPU: 2
- Memory: 2Gi

### MCP Server (Moderate Traffic)
- Min instances: 1
- Max instances: 10
- CPU: 1
- Memory: 1Gi

## Security Best Practices

1. **Never commit API keys** - Use environment variables
2. **Enable Cloud Run authentication** for production
3. **Use Secret Manager** for sensitive data
4. **Set up VPC connector** for database access
5. **Enable Cloud Armor** for DDoS protection

## Troubleshooting

### Service Not Starting

```bash
# Check logs
gcloud run services logs read SERVICE_NAME --region us-central1

# Check service status
gcloud run services describe SERVICE_NAME --region us-central1
```

### Permission Errors

```bash
# Grant Cloud Run invoker role for public access
gcloud run services add-iam-policy-binding SERVICE_NAME \
  --region us-central1 \
  --member="allUsers" \
  --role="roles/run.invoker"
```

### Cold Start Issues

Increase minimum instances:
```bash
gcloud run services update SERVICE_NAME \
  --region us-central1 \
  --min-instances 2
```

## Cost Optimization

1. **Use minimum instances wisely** - Only for critical services
2. **Set appropriate CPU/memory** - Don't over-provision
3. **Enable request timeout** - Prevent hanging requests
4. **Use Cloud CDN** for static assets

## Support

For issues or questions:
- GitHub Issues: [water-futures-ai/issues](https://github.com/your-org/water-futures-ai/issues)
- Documentation: [docs.water-futures.ai](https://docs.water-futures.ai)

## License

MIT License - See LICENSE file for details.