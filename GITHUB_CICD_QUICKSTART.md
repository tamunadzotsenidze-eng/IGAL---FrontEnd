# GitHub CI/CD Quick Start Guide

This guide will help you set up **automatic deployment** from GitHub to Google Cloud Run.

## What You'll Get

When set up, **every time you push to GitHub**, your app will automatically:
1. Build a new Docker image
2. Push it to Artifact Registry
3. Deploy to Cloud Run
4. Be live in production in ~5-10 minutes

No manual deployment needed!

---

## Prerequisites

1. ✅ Two GitHub repositories (backend and frontend)
2. ✅ Google Cloud Project: `igal-ai-project`
3. ✅ Docker files and cloudbuild.yaml (already created)

---

## Quick Setup (3 Steps)

### Step 1: Install Google Cloud Build GitHub App

1. Go to https://github.com/apps/google-cloud-build
2. Click **"Configure"**
3. Select your GitHub account/organization
4. Select your IGAL backend and frontend repositories
5. Click **"Install & Authorize"**

### Step 2: Run the Automated Setup Script

```bash
cd /Users/tiko/Desktop/IGAL
./setup_github_cicd.sh
```

The script will:
- Connect your local repos to GitHub
- Grant necessary permissions
- Create Cloud Build triggers
- Set up automatic deployment

### Step 3: Push to GitHub

```bash
# Backend
cd /Users/tiko/Desktop/IGAL/backend
git add .
git commit -m "Enable CI/CD"
git push origin main

# Frontend
cd /Users/tiko/Desktop/IGAL/frontend
git add .
git commit -m "Enable CI/CD"
git push origin main
```

That's it! Your apps will automatically deploy.

---

## Manual Setup (If Script Doesn't Work)

### 1. Connect GitHub Repositories

```bash
# Backend
cd /Users/tiko/Desktop/IGAL/backend
git remote add origin https://github.com/YOUR_USERNAME/igal-backend.git
git branch -M main
git push -u origin main

# Frontend
cd /Users/tiko/Desktop/IGAL/frontend
git remote add origin https://github.com/YOUR_USERNAME/igal-frontend.git
git branch -M main
git push -u origin main
```

### 2. Create Cloud Build Triggers via Console

1. **Open Cloud Build Triggers**:
   https://console.cloud.google.com/cloud-build/triggers?project=igal-ai-project

2. **Click "CREATE TRIGGER" for Backend**:
   - Name: `igal-backend-deploy`
   - Event: Push to branch
   - Repository: Select your backend repository
   - Branch: `^main$`
   - Configuration: Cloud Build configuration file
   - Location: `/cloudbuild.yaml`
   - Substitution variables:
     - `_REGION`: `europe-west3`
     - `_CLOUD_SQL_CONNECTION_NAME`: `igal-ai-project:europe-west3:igal-db-instance`
     - `_SECRET_KEY_SECRET`: `igal-secret-key`
     - `_OPENAI_API_KEY_SECRET`: `igal-openai-api-key`
     - `_DB_PASSWORD_SECRET`: `igal-db-password`

3. **Click "CREATE TRIGGER" for Frontend**:
   - Name: `igal-frontend-deploy`
   - Event: Push to branch
   - Repository: Select your frontend repository
   - Branch: `^main$`
   - Configuration: Cloud Build configuration file
   - Location: `/cloudbuild.yaml`
   - Substitution variables:
     - `_REGION`: `europe-west3`
     - `_BACKEND_URL`: (Get from backend Cloud Run service URL)

### 3. Get Backend URL

```bash
gcloud run services describe igal-backend --region=europe-west3 --format='value(status.url)'
```

Use this URL in the frontend trigger's `_BACKEND_URL` variable.

---

## How It Works

```
Developer pushes to GitHub
         ↓
GitHub webhook triggers Cloud Build
         ↓
Cloud Build runs cloudbuild.yaml:
  1. Builds Docker image
  2. Pushes to Artifact Registry
  3. Deploys to Cloud Run
         ↓
Application live in production!
```

---

## Testing the Pipeline

### Monitor Build Progress

```bash
# List ongoing builds
gcloud builds list --ongoing

# View build logs
gcloud builds log $(gcloud builds list --limit=1 --format="value(id)")

# Or view in console
open "https://console.cloud.google.com/cloud-build/builds?project=igal-ai-project"
```

### Check Deployment Status

```bash
# Backend
gcloud run services describe igal-backend --region=europe-west3

# Frontend
gcloud run services describe igal-frontend --region=europe-west3
```

---

## Troubleshooting

### Build Trigger Not Firing

**Problem**: Pushed to GitHub but no build started

**Solution**:
1. Check trigger is enabled:
   https://console.cloud.google.com/cloud-build/triggers?project=igal-ai-project
2. Verify branch name matches trigger pattern (should be `main`)
3. Check GitHub App has repository access:
   https://github.com/settings/installations

### Permission Denied Errors

**Problem**: Build fails with permission errors

**Solution**:
```bash
PROJECT_NUMBER=$(gcloud projects describe igal-ai-project --format='value(projectNumber)')

gcloud projects add-iam-policy-binding igal-ai-project \
    --member="serviceAccount:$PROJECT_NUMBER@cloudbuild.gserviceaccount.com" \
    --role="roles/run.admin"

gcloud projects add-iam-policy-binding igal-ai-project \
    --member="serviceAccount:$PROJECT_NUMBER@cloudbuild.gserviceaccount.com" \
    --role="roles/iam.serviceAccountUser"
```

### Deployment Fails

**Problem**: Build succeeds but deployment fails

**Solution**:
```bash
# Check Cloud Run logs
gcloud run services logs read igal-backend --region=europe-west3 --limit=50

# Verify secrets exist
gcloud secrets list

# Test deployment manually
gcloud run deploy igal-backend \
    --image europe-west3-docker.pkg.dev/igal-ai-project/igal-backend-repo/igal-backend:latest \
    --region=europe-west3
```

---

## Useful Commands

```bash
# List all triggers
gcloud builds triggers list

# Delete a trigger
gcloud builds triggers delete TRIGGER_NAME

# Run a trigger manually
gcloud builds triggers run TRIGGER_NAME

# View recent builds
gcloud builds list --limit=10

# View service URL
gcloud run services describe igal-backend --region=europe-west3 --format='value(status.url)'
```

---

## Branch Strategy (Recommended)

### Development Branch
Create a `dev` trigger for the `dev` branch:
```bash
git checkout -b dev
git push origin dev
```

Create trigger for `dev` branch that deploys to a separate dev service.

### Production Branch
Main branch (`main`) deploys to production.

### Workflow
```
feature branch → dev branch → main branch
     ↓              ↓            ↓
   local         dev env      production
```

---

## Cost Optimization

- **Free Tier**: 120 build-minutes/day
- **After Free Tier**: $0.003/build-minute
- **Typical build time**: 8-10 minutes
- **Cost per deployment**: ~$0.03-0.06

To reduce costs:
1. Only trigger on `main` branch (not all branches)
2. Skip CI for documentation changes (use `[skip ci]` in commit message)
3. Use caching in Dockerfile

---

## Next Steps

After CI/CD is working:

1. **Add Tests to Pipeline**
   - Add test step to `cloudbuild.yaml`
   - Run tests before deployment

2. **Set up Staging Environment**
   - Create separate Cloud Run services
   - Deploy `dev` branch to staging

3. **Custom Domain**
   - Map igal.ge to your Cloud Run services
   - Configure SSL/TLS

4. **Monitoring**
   - Set up Cloud Monitoring alerts
   - Configure error reporting

---

## Support

- **Cloud Build Docs**: https://cloud.google.com/build/docs
- **Cloud Run Docs**: https://cloud.google.com/run/docs
- **GitHub Integration**: https://cloud.google.com/build/docs/automating-builds/github/build-repos-from-github

For issues, check:
https://console.cloud.google.com/cloud-build/builds?project=igal-ai-project

---

**Last Updated**: November 18, 2025
**Project**: IGAL AI Project (igal-ai-project)
