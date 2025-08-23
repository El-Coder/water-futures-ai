# 🚀 GitHub Deployment Setup Guide

## Step 1: Setup Google Cloud Project

### 1.1 Create GCP Project (if not exists)
```bash
gcloud projects create water-futures-ai --name="Water Futures AI"
gcloud config set project water-futures-ai

# Enable billing (required for Cloud Run)
# Visit: https://console.cloud.google.com/billing
```

### 1.2 Enable Required APIs
```bash
gcloud services enable \
  run.googleapis.com \
  artifactregistry.googleapis.com \
  cloudbuild.googleapis.com \
  secretmanager.googleapis.com
```

### 1.3 Create Artifact Registry
```bash
gcloud artifacts repositories create water-futures \
  --repository-format=docker \
  --location=us-central1 \
  --description="Water Futures AI Docker images"
```

## Step 2: Create Service Account for GitHub Actions

### 2.1 Create Service Account
```bash
gcloud iam service-accounts create github-actions \
  --display-name="GitHub Actions Deploy"
```

### 2.2 Grant Permissions
```bash
PROJECT_ID=water-futures-ai
SERVICE_ACCOUNT=github-actions@${PROJECT_ID}.iam.gserviceaccount.com

# Cloud Run Admin
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SERVICE_ACCOUNT" \
  --role="roles/run.admin"

# Artifact Registry Admin
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SERVICE_ACCOUNT" \
  --role="roles/artifactregistry.admin"

# Service Account User
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SERVICE_ACCOUNT" \
  --role="roles/iam.serviceAccountUser"

# Storage Admin (for Container Registry)
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SERVICE_ACCOUNT" \
  --role="roles/storage.admin"
```

### 2.3 Create Service Account Key
```bash
gcloud iam service-accounts keys create ~/github-key.json \
  --iam-account=github-actions@water-futures-ai.iam.gserviceaccount.com
```

## Step 3: Add Secrets to GitHub

### 3.1 Navigate to Your Repository Settings
1. Go to your GitHub repository
2. Click on **Settings** tab
3. In the left sidebar, click **Secrets and variables** → **Actions**

### 3.2 Add the Following Secrets

Click **New repository secret** for each:

#### Required Secrets:

| Secret Name | Value | How to Get |
|------------|-------|------------|
| `GCP_SA_KEY` | Contents of `~/github-key.json` | `cat ~/github-key.json` then copy entire JSON |
| `ANTHROPIC_API_KEY` | `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` | From Anthropic Console |
| `ALPACA_API_KEY` | `PKBGCEN19LBO7XSXRV0P` | From Alpaca Dashboard |
| `ALPACA_SECRET_KEY` | `c4Mbdt3J0cLKPaeUJecD6Db1sTsmiNudz0QdfyaP` | From Alpaca Dashboard |
| `CROSSMINT_API_KEY` | `sk_staging_9ymj6pzDVzTXAJxEHx2Eiaudh7Bv9tAZYkbC7oJyXxQUupx3fi4pQyNmShEZ7BMDSkT2DGw8EyxcPUvqLyVoJTP3DQQ2JQya8iB7eTK95tWKHDK9xMGapfbgoYBvY8ettfPjCw2Sm9kxEMxEe3iWAvWEPrW3PuQUXAzjppFbauu5uHNK1rDdiQ2XoKecGbMre99jNGmdVQkabJ84QYPbzMBj` | From Crossmint Dashboard |
| `UNCLE_SAM_WALLET_ADDRESS` | `0x732278e9D7A02a746dcF38108dA30647CDb91217` | Your wallet address |

### 3.3 How to Add Each Secret:
1. Click **New repository secret**
2. Enter the **Name** exactly as shown above
3. Paste the **Value**
4. Click **Add secret**

## Step 4: Update GitHub Actions Workflow

The workflow is already created at `.github/workflows/deploy-fix.yml`

To use it, either:
- Rename it to `deploy.yml` (replacing the old one)
- Or trigger it manually from GitHub Actions tab

## Step 5: Test Deployment

### 5.1 Manual Trigger (Recommended for First Time)
1. Go to **Actions** tab in your repository
2. Select **Deploy to Cloud Run (Fixed)** workflow
3. Click **Run workflow** → **Run workflow**

### 5.2 Automatic Trigger
```bash
git add .
git commit -m "Setup Cloud Run deployment"
git push origin main
```

## Step 6: Verify Deployment

### 6.1 Check GitHub Actions
- Go to **Actions** tab
- Click on the running workflow
- Watch the logs for any errors

### 6.2 Check Cloud Run Console
```bash
# Or visit: https://console.cloud.google.com/run?project=water-futures-ai
gcloud run services list --region=us-central1
```

### 6.3 Get Service URLs
```bash
# Backend URL
gcloud run services describe water-futures-backend \
  --region=us-central1 \
  --format='value(status.url)'

# MCP Server URL
gcloud run services describe water-futures-mcp \
  --region=us-central1 \
  --format='value(status.url)'
```

## Troubleshooting

### Error: "Permission denied"
```bash
# Ensure service account has correct permissions
gcloud projects get-iam-policy water-futures-ai \
  --flatten="bindings[].members" \
  --filter="bindings.members:github-actions@water-futures-ai.iam.gserviceaccount.com"
```

### Error: "API not enabled"
```bash
# Enable all required APIs
gcloud services enable \
  run.googleapis.com \
  artifactregistry.googleapis.com \
  containerregistry.googleapis.com \
  cloudbuild.googleapis.com
```

### Error: "Artifact Registry not found"
```bash
# Create Artifact Registry
gcloud artifacts repositories create water-futures \
  --repository-format=docker \
  --location=us-central1
```

### Error: "Invalid key format"
Make sure when copying the service account key JSON:
1. Copy the ENTIRE content including `{` and `}`
2. Don't add any extra whitespace or newlines
3. Paste it exactly as is into the GitHub secret

## Clean Up (After Adding to GitHub)

```bash
# Delete local service account key for security
rm ~/github-key.json
```

## Quick Setup Script

Run this to do everything automatically:
```bash
chmod +x setup-gcp.sh
./setup-gcp.sh water-futures-ai
```

Then manually add the secrets to GitHub as described above.

## Support

If you encounter issues:
1. Check the GitHub Actions logs
2. Check Cloud Run logs: `gcloud run services logs read SERVICE_NAME --region=us-central1`
3. Verify all secrets are set correctly in GitHub
4. Ensure billing is enabled on your GCP project