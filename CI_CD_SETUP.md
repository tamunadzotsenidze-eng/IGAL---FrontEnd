# IGAL - CI/CD Setup Guide

Complete guide for setting up automated deployments for both backend and frontend on Google Cloud Platform.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Architecture Overview](#architecture-overview)
3. [Backend CI/CD Setup](#backend-cicd-setup)
4. [Frontend CI/CD Setup](#frontend-cicd-setup)
5. [Cloud Build Triggers](#cloud-build-triggers)
6. [Testing the Pipeline](#testing-the-pipeline)
7. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Already Completed
- ✅ Google Cloud Project: `igal-ai-project`
- ✅ Cloud SQL database: `igal-db-instance`
- ✅ Secret Manager with credentials
- ✅ Artifact Registry repositories:
  - `igal-backend-repo` (europe-west3)
  - `igal-frontend-repo` (europe-west3)
- ✅ IAM permissions configured
- ✅ Dockerfile and cloudbuild.yaml for both projects

### Required Setup
- [ ] Git repository (GitHub, GitLab, or Cloud Source Repositories)
- [ ] Connect repository to Cloud Build
- [ ] Create Cloud Build triggers

---

## Architecture Overview

```
┌─────────────┐
│  Developer  │
└──────┬──────┘
       │ git push
       ▼
┌─────────────────┐
│ Git Repository  │
│ (GitHub/GitLab) │
└──────┬──────────┘
       │ webhook
       ▼
┌─────────────────┐
│  Cloud Build    │ ◄── Triggers automatically on push
│  (CI/CD)        │
└──────┬──────────┘
       │
       ├─────────────┬─────────────┐
       ▼             ▼             ▼
┌──────────┐  ┌──────────┐  ┌──────────┐
│  Build   │  │  Test    │  │  Deploy  │
│  Image   │  │  (TODO)  │  │  to Run  │
└──────────┘  └──────────┘  └──────────┘
       │                           │
       ▼                           ▼
┌──────────────┐          ┌──────────────┐
│  Artifact    │          │  Cloud Run   │
│  Registry    │          │  (Production)│
└──────────────┘          └──────────────┘
```

---

## Backend CI/CD Setup

### 1. Repository Structure

Ensure your backend repository has:
```
backend/
├── Dockerfile
├── cloudbuild.yaml
├── requirements.txt
├── manage.py
├── igal/
└── ... (other Django files)
```

### 2. Cloud Build Configuration

The `cloudbuild.yaml` is already configured to:
1. Build Docker image from Dockerfile
2. Push to Artifact Registry (`europe-west3-docker.pkg.dev/igal-ai-project/igal-backend-repo`)
3. Deploy to Cloud Run (`igal-backend` service)
4. Run database migrations (optional step)

**Key Configuration**:
- **Region**: `europe-west3` (Frankfurt)
- **Memory**: 2 GiB
- **CPU**: 2 cores
- **Secrets**: Mounted from Secret Manager
- **Cloud SQL**: Connected via Unix socket

### 3. Manual Deployment (One-Time)

Before setting up automated triggers, test manual deployment:

```bash
cd /Users/tiko/Desktop/IGAL/backend

# Build and deploy using Cloud Build
gcloud builds submit --tag europe-west3-docker.pkg.dev/igal-ai-project/igal-backend-repo/igal-backend:latest

# Deploy to Cloud Run
gcloud run deploy igal-backend \
  --image europe-west3-docker.pkg.dev/igal-ai-project/igal-backend-repo/igal-backend:latest \
  --region=europe-west3 \
  --platform=managed \
  --allow-unauthenticated \
  --memory=2Gi \
  --cpu=2 \
  --set-env-vars="DEBUG=False,RAG_ENABLED=True,CLOUD_RUN_SERVICE=true,DB_NAME=igal_db,DB_USER=igal_user" \
  --set-secrets="SECRET_KEY=igal-secret-key:latest,OPENAI_API_KEY=igal-openai-api-key:latest,DB_PASSWORD=igal-db-password:latest" \
  --set-cloudsql-instances=igal-ai-project:europe-west3:igal-db-instance
```

---

## Frontend CI/CD Setup

### 1. Repository Structure

Ensure your frontend repository has:
```
frontend/
├── Dockerfile (✅ Created)
├── cloudbuild.yaml (✅ Created)
├── next.config.js (✅ Updated with standalone output)
├── package.json
├── pages/
├── components/
└── ... (other Next.js files)
```

### 2. Cloud Build Configuration

The `cloudbuild.yaml` is configured to:
1. Build Next.js Docker image
2. Push to Artifact Registry (`europe-west3-docker.pkg.dev/igal-ai-project/igal-frontend-repo`)
3. Deploy to Cloud Run (`igal-frontend` service)

**Key Configuration**:
- **Region**: `europe-west3` (Frankfurt)
- **Memory**: 512 MiB
- **CPU**: 1 core
- **Environment Variables**: API URL, app configuration

### 3. Update Backend URL

After backend is deployed, update the frontend configuration:

```bash
# Get backend URL
BACKEND_URL=$(gcloud run services describe igal-backend --region=europe-west3 --format='value(status.url)')
echo "Backend URL: $BACKEND_URL"

# Update frontend cloudbuild.yaml
# Replace _BACKEND_URL with actual URL
```

---

## Cloud Build Triggers

### Option 1: GitHub Integration (Recommended)

#### Connect GitHub Repository

1. **Go to Cloud Build Triggers**:
   ```bash
   open "https://console.cloud.google.com/cloud-build/triggers?project=igal-ai-project"
   ```

2. **Connect Repository**:
   - Click "Connect Repository"
   - Select "GitHub"
   - Authenticate with GitHub
   - Select your IGAL repositories

#### Create Backend Trigger

1. **Click "Create Trigger"**
2. **Configure**:
   - **Name**: `igal-backend-deploy`
   - **Description**: Auto-deploy backend on push to main
   - **Event**: Push to branch
   - **Source**:
     - Repository: `your-repo/igal-backend`
     - Branch: `^main$`
   - **Configuration**:
     - Type: Cloud Build configuration file
     - Location: `/cloudbuild.yaml`
   - **Substitution variables**:
     - `_REGION`: `europe-west3`
     - `_CLOUD_SQL_CONNECTION_NAME`: `igal-ai-project:europe-west3:igal-db-instance`
     - `_SECRET_KEY_SECRET`: `igal-secret-key`
     - `_OPENAI_API_KEY_SECRET`: `igal-openai-api-key`
     - `_DB_PASSWORD_SECRET`: `igal-db-password`

3. **Click "Create"**

#### Create Frontend Trigger

1. **Click "Create Trigger"**
2. **Configure**:
   - **Name**: `igal-frontend-deploy`
   - **Description**: Auto-deploy frontend on push to main
   - **Event**: Push to branch
   - **Source**:
     - Repository: `your-repo/igal-frontend`
     - Branch: `^main$`
   - **Configuration**:
     - Type: Cloud Build configuration file
     - Location: `/cloudbuild.yaml`
   - **Substitution variables**:
     - `_REGION`: `europe-west3`
     - `_BACKEND_URL`: `https://igal-backend-XXXXX-ew.a.run.app`

3. **Click "Create"**

### Option 2: Manual Trigger (CLI)

#### Backend Deployment
```bash
cd /Users/tiko/Desktop/IGAL/backend
gcloud builds submit --config=cloudbuild.yaml
```

#### Frontend Deployment
```bash
cd /Users/tiko/Desktop/IGAL/frontend
gcloud builds submit --config=cloudbuild.yaml \
  --substitutions=_BACKEND_URL="https://igal-backend-XXXXX-ew.a.run.app"
```

---

## Testing the Pipeline

### 1. Test Backend Pipeline

```bash
# Make a small change
cd /Users/tiko/Desktop/IGAL/backend
echo "# Test change" >> README.md

# Commit and push
git add .
git commit -m "Test CI/CD pipeline"
git push origin main

# Monitor build
gcloud builds list --ongoing
gcloud builds log $(gcloud builds list --limit=1 --format="value(id)")
```

### 2. Test Frontend Pipeline

```bash
# Make a small change
cd /Users/tiko/Desktop/IGAL/frontend
echo "# Test change" >> README.md

# Commit and push
git add .
git commit -m "Test CI/CD pipeline"
git push origin main

# Monitor build
gcloud builds list --ongoing
```

### 3. Verify Deployment

```bash
# Get backend URL
gcloud run services describe igal-backend --region=europe-west3 --format='value(status.url)'

# Get frontend URL
gcloud run services describe igal-frontend --region=europe-west3 --format='value(status.url)'

# Test endpoints
curl https://igal-backend-XXXXX-ew.a.run.app/health/
curl https://igal-frontend-XXXXX-ew.a.run.app/
```

---

## Deployment Workflow

### Development Workflow

```bash
# 1. Create feature branch
git checkout -b feature/new-feature

# 2. Make changes
# ... code changes ...

# 3. Test locally
# Backend: python manage.py runserver
# Frontend: npm run dev

# 4. Commit changes
git add .
git commit -m "Add new feature"

# 5. Push to feature branch
git push origin feature/new-feature

# 6. Create pull request
# ... review and approve ...

# 7. Merge to main (triggers automatic deployment)
git checkout main
git pull origin main
```

### Production Deployment

Once merged to `main`, the CI/CD pipeline automatically:

**Backend**:
1. ⏱️ Builds Docker image (~5-8 minutes)
2. ⏱️ Pushes to Artifact Registry (~1-2 minutes)
3. ⏱️ Deploys to Cloud Run (~2-3 minutes)
4. ⏱️ Runs migrations (~30 seconds)

**Frontend**:
1. ⏱️ Builds Next.js application (~3-5 minutes)
2. ⏱️ Pushes to Artifact Registry (~1 minute)
3. ⏱️ Deploys to Cloud Run (~1-2 minutes)

**Total Time**: ~10-15 minutes from push to production

---

## Environment Variables

### Backend Environment Variables

Configured in `cloudbuild.yaml` and Cloud Run:
- `DEBUG`: `False` (production)
- `RAG_ENABLED`: `True`
- `CLOUD_RUN_SERVICE`: `true`
- `DB_NAME`: `igal_db`
- `DB_USER`: `igal_user`
- `SECRET_KEY`: From Secret Manager
- `OPENAI_API_KEY`: From Secret Manager
- `DB_PASSWORD`: From Secret Manager

### Frontend Environment Variables

Configured in `cloudbuild.yaml` and Cloud Run:
- `NEXT_PUBLIC_API_URL`: Backend URL
- `NEXT_PUBLIC_API_BASE`: `/api`
- `NEXT_PUBLIC_APP_NAME`: `IGAL`
- `NEXT_PUBLIC_APP_VERSION`: `1.0.0`
- `NEXT_PUBLIC_ENABLE_ANALYTICS`: `false`
- `NEXT_PUBLIC_ENABLE_AUTH`: `true`

---

## Monitoring and Logging

### View Deployment Logs

```bash
# Backend logs
gcloud run services logs tail igal-backend --region=europe-west3

# Frontend logs
gcloud run services logs tail igal-frontend --region=europe-west3

# Build logs
gcloud builds log BUILD_ID
```

### Monitor Service Health

```bash
# Backend health check
curl https://igal-backend-XXXXX-ew.a.run.app/health/

# View service details
gcloud run services describe igal-backend --region=europe-west3
gcloud run services describe igal-frontend --region=europe-west3
```

### Cloud Console Dashboards

- **Cloud Build**: https://console.cloud.google.com/cloud-build/builds?project=igal-ai-project
- **Cloud Run**: https://console.cloud.google.com/run?project=igal-ai-project
- **Artifact Registry**: https://console.cloud.google.com/artifacts?project=igal-ai-project
- **Cloud SQL**: https://console.cloud.google.com/sql/instances?project=igal-ai-project

---

## Troubleshooting

### Build Failures

#### Permission Denied Errors
```bash
# Grant necessary permissions
gcloud projects add-iam-policy-binding igal-ai-project \
  --member="serviceAccount:613144374930@cloudbuild.gserviceaccount.com" \
  --role="roles/artifactregistry.writer"

gcloud projects add-iam-policy-binding igal-ai-project \
  --member="serviceAccount:613144374930@cloudbuild.gserviceaccount.com" \
  --role="roles/run.admin"
```

#### Docker Build Fails
```bash
# Test Dockerfile locally
cd /Users/tiko/Desktop/IGAL/backend
docker build -t test-image .

# Check Cloud Build logs
gcloud builds log BUILD_ID
```

### Deployment Failures

#### Cloud Run Deployment Error
```bash
# Check service status
gcloud run services describe igal-backend --region=europe-west3

# View recent logs
gcloud run services logs read igal-backend --region=europe-west3 --limit=100
```

#### Secret Access Denied
```bash
# Grant secret access to Cloud Run service account
gcloud secrets add-iam-policy-binding igal-secret-key \
  --member="serviceAccount:613144374930-compute@developer.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

### Database Connection Issues

```bash
# Verify Cloud SQL instance is running
gcloud sql instances describe igal-db-instance

# Check Cloud SQL connection name
gcloud sql instances describe igal-db-instance \
  --format='value(connectionName)'

# Test connection from Cloud Run
gcloud run jobs execute igal-migrate --region=europe-west3 --wait
```

---

## Rollback Procedure

If a deployment fails or introduces bugs:

### Quick Rollback

```bash
# List recent revisions
gcloud run revisions list --service=igal-backend --region=europe-west3

# Rollback to previous revision
gcloud run services update-traffic igal-backend \
  --region=europe-west3 \
  --to-revisions=PREVIOUS_REVISION=100
```

### Redeploy Specific Version

```bash
# Deploy specific image tag
gcloud run deploy igal-backend \
  --image europe-west3-docker.pkg.dev/igal-ai-project/igal-backend-repo/igal-backend:COMMIT_SHA \
  --region=europe-west3
```

---

## Cost Optimization

### Current Configuration

| Service | Cost (Monthly) | Notes |
|---------|---------------|-------|
| Cloud Build | $0.003/min after 120 min free | ~$10-20/month |
| Artifact Registry | $0.10/GB/month | ~$1-2/month |
| Cloud Run (Backend) | ~$50-100 | 2 CPU, 2Gi, min 1 instance |
| Cloud Run (Frontend) | ~$10-20 | 1 CPU, 512Mi, min 0 instances |
| **Total CI/CD** | **~$71-142/month** | Includes compute + storage |

### Optimization Tips

1. **Reduce Cloud Build time**:
   - Use Docker layer caching
   - Optimize Dockerfile with multi-stage builds
   - Minimize dependencies

2. **Frontend scaling**:
   - Set `min-instances=0` for dev/staging
   - Use CDN for static assets

3. **Build frequency**:
   - Use branch protections
   - Only build on main branch
   - Skip builds for documentation changes

---

## Next Steps

- [ ] Connect Git repositories to Cloud Build
- [ ] Create build triggers for automatic deployment
- [ ] Test deployment pipeline with a small change
- [ ] Set up custom domain (igal.ge)
- [ ] Configure SSL/TLS certificates
- [ ] Add staging environment
- [ ] Set up monitoring and alerting
- [ ] Implement automated testing in pipeline

---

## Support Resources

- **Cloud Build Documentation**: https://cloud.google.com/build/docs
- **Cloud Run Documentation**: https://cloud.google.com/run/docs
- **Artifact Registry Documentation**: https://cloud.google.com/artifact-registry/docs
- **Project Console**: https://console.cloud.google.com/home/dashboard?project=igal-ai-project

---

**Last Updated**: November 18, 2025
**Status**: CI/CD configuration ready, awaiting trigger setup
**Version**: 1.0
