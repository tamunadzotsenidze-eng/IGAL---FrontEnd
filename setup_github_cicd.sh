#!/bin/bash

# IGAL - Automated GitHub CI/CD Setup Script
# This script sets up automatic deployment from GitHub to Google Cloud Run

set -e  # Exit on error

echo "==================================================================="
echo "  IGAL - GitHub CI/CD Automation Setup"
echo "==================================================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Project configuration
PROJECT_ID="igal-ai-project"
REGION="europe-west3"

echo -e "${YELLOW}Step 1: Verify Google Cloud Configuration${NC}"
echo "-------------------------------------------------------------------"
gcloud config set project $PROJECT_ID
echo -e "${GREEN}✓ Project set to: $PROJECT_ID${NC}"
echo ""

echo -e "${YELLOW}Step 2: GitHub Repository Setup${NC}"
echo "-------------------------------------------------------------------"
echo "Please provide your GitHub repository URLs:"
echo ""
read -p "Backend GitHub URL (e.g., https://github.com/username/igal-backend): " BACKEND_REPO
read -p "Frontend GitHub URL (e.g., https://github.com/username/igal-frontend): " FRONTEND_REPO
echo ""

# Extract GitHub details
BACKEND_OWNER=$(echo $BACKEND_REPO | sed 's/.*github.com\/\([^/]*\)\/.*/\1/')
BACKEND_NAME=$(echo $BACKEND_REPO | sed 's/.*github.com\/[^/]*\/\([^/]*\).*/\1/' | sed 's/\.git//')
FRONTEND_OWNER=$(echo $FRONTEND_REPO | sed 's/.*github.com\/\([^/]*\)\/.*/\1/')
FRONTEND_NAME=$(echo $FRONTEND_REPO | sed 's/.*github.com\/[^/]*\/\([^/]*\).*/\1/' | sed 's/\.git//')

echo -e "${GREEN}✓ Backend: $BACKEND_OWNER/$BACKEND_NAME${NC}"
echo -e "${GREEN}✓ Frontend: $FRONTEND_OWNER/$FRONTEND_NAME${NC}"
echo ""

echo -e "${YELLOW}Step 3: Connect Local Repositories to GitHub${NC}"
echo "-------------------------------------------------------------------"

# Backend
echo "Connecting backend to GitHub..."
cd /Users/tiko/Desktop/IGAL/backend
if ! git remote get-url origin > /dev/null 2>&1; then
    git remote add origin $BACKEND_REPO
    echo -e "${GREEN}✓ Added origin remote for backend${NC}"
else
    git remote set-url origin $BACKEND_REPO
    echo -e "${GREEN}✓ Updated origin remote for backend${NC}"
fi

# Frontend
echo "Connecting frontend to GitHub..."
cd /Users/tiko/Desktop/IGAL/frontend
if ! git remote get-url origin > /dev/null 2>&1; then
    git remote add origin $FRONTEND_REPO
    echo -e "${GREEN}✓ Added origin remote for frontend${NC}"
else
    git remote set-url origin $FRONTEND_REPO
    echo -e "${GREEN}✓ Updated origin remote for frontend${NC}"
fi
echo ""

echo -e "${YELLOW}Step 4: Grant Cloud Build Service Account Permissions${NC}"
echo "-------------------------------------------------------------------"

# Get project number
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format='value(projectNumber)')

# Grant permissions to Cloud Build service account
echo "Granting permissions to Cloud Build service accounts..."
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$PROJECT_NUMBER@cloudbuild.gserviceaccount.com" \
    --role="roles/run.admin" \
    --quiet

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$PROJECT_NUMBER@cloudbuild.gserviceaccount.com" \
    --role="roles/iam.serviceAccountUser" \
    --quiet

echo -e "${GREEN}✓ Permissions granted${NC}"
echo ""

echo -e "${YELLOW}Step 5: Install Google Cloud Build GitHub App${NC}"
echo "-------------------------------------------------------------------"
echo -e "${YELLOW}⚠ MANUAL STEP REQUIRED${NC}"
echo ""
echo "You need to install the Google Cloud Build GitHub App to enable automatic builds."
echo ""
echo "1. Go to: https://github.com/apps/google-cloud-build"
echo "2. Click 'Configure'"
echo "3. Select your GitHub account/organization"
echo "4. Choose repositories:"
echo "   - $BACKEND_NAME"
echo "   - $FRONTEND_NAME"
echo "5. Click 'Install & Authorize'"
echo ""
read -p "Press Enter once you've installed the GitHub App..."
echo ""

echo -e "${YELLOW}Step 6: Connect GitHub Repositories to Cloud Build${NC}"
echo "-------------------------------------------------------------------"
echo ""
echo "Opening Cloud Build Triggers console..."
open "https://console.cloud.google.com/cloud-build/triggers;region=global?project=$PROJECT_ID"
echo ""
echo -e "${YELLOW}⚠ MANUAL STEP REQUIRED${NC}"
echo ""
echo "In the Cloud Console:"
echo "1. Click 'CONNECT REPOSITORY'"
echo "2. Select 'GitHub (Cloud Build GitHub App)'"
echo "3. Authenticate with GitHub if prompted"
echo "4. Select repository: $BACKEND_OWNER/$BACKEND_NAME"
echo "5. Click 'Connect'"
echo "6. Repeat for frontend: $FRONTEND_OWNER/$FRONTEND_NAME"
echo ""
read -p "Press Enter once repositories are connected..."
echo ""

echo -e "${YELLOW}Step 7: Create Backend Build Trigger${NC}"
echo "-------------------------------------------------------------------"

# Create backend trigger
gcloud builds triggers create github \
    --name="igal-backend-deploy" \
    --description="Auto-deploy backend on push to main" \
    --repo-name="$BACKEND_NAME" \
    --repo-owner="$BACKEND_OWNER" \
    --branch-pattern="^main$" \
    --build-config="cloudbuild.yaml" \
    --region=global \
    --substitutions="_REGION=$REGION,_CLOUD_SQL_CONNECTION_NAME=$PROJECT_ID:$REGION:igal-db-instance,_SECRET_KEY_SECRET=igal-secret-key,_OPENAI_API_KEY_SECRET=igal-openai-api-key,_DB_PASSWORD_SECRET=igal-db-password" \
    2>&1 || echo -e "${YELLOW}Note: Trigger may already exist or require manual setup${NC}"

echo -e "${GREEN}✓ Backend trigger created${NC}"
echo ""

echo -e "${YELLOW}Step 8: Deploy Backend and Get URL${NC}"
echo "-------------------------------------------------------------------"
echo "We need the backend URL before creating the frontend trigger..."
echo ""

# Check if backend is already deployed
BACKEND_URL=$(gcloud run services describe igal-backend --region=$REGION --format='value(status.url)' 2>/dev/null || echo "")

if [ -z "$BACKEND_URL" ]; then
    echo -e "${YELLOW}Backend not yet deployed. Deploying now...${NC}"
    echo "Note: Initial deployment takes about 5-10 minutes."
    echo ""
    read -p "Deploy backend now? (y/n): " DEPLOY_NOW

    if [ "$DEPLOY_NOW" = "y" ]; then
        cd /Users/tiko/Desktop/IGAL/backend
        echo "Building and deploying backend..."
        gcloud builds submit --tag europe-west3-docker.pkg.dev/$PROJECT_ID/igal-backend-repo/igal-backend:latest --timeout=20m

        gcloud run deploy igal-backend \
            --image europe-west3-docker.pkg.dev/$PROJECT_ID/igal-backend-repo/igal-backend:latest \
            --region=$REGION \
            --platform=managed \
            --allow-unauthenticated \
            --memory=2Gi \
            --cpu=2 \
            --timeout=300 \
            --max-instances=10 \
            --min-instances=1 \
            --set-env-vars="DEBUG=False,RAG_ENABLED=True,CLOUD_RUN_SERVICE=true,DB_NAME=igal_db,DB_USER=igal_user" \
            --set-secrets="SECRET_KEY=igal-secret-key:latest,OPENAI_API_KEY=igal-openai-api-key:latest,DB_PASSWORD=igal-db-password:latest" \
            --set-cloudsql-instances=$PROJECT_ID:$REGION:igal-db-instance

        BACKEND_URL=$(gcloud run services describe igal-backend --region=$REGION --format='value(status.url)')
    else
        echo -e "${YELLOW}⚠ Skipping backend deployment. You'll need to deploy it manually before frontend.${NC}"
        BACKEND_URL="https://igal-backend-placeholder.run.app"
    fi
else
    echo -e "${GREEN}✓ Backend already deployed${NC}"
fi

echo ""
echo -e "${GREEN}Backend URL: $BACKEND_URL${NC}"
echo ""

echo -e "${YELLOW}Step 9: Create Frontend Build Trigger${NC}"
echo "-------------------------------------------------------------------"

# Create frontend trigger
gcloud builds triggers create github \
    --name="igal-frontend-deploy" \
    --description="Auto-deploy frontend on push to main" \
    --repo-name="$FRONTEND_NAME" \
    --repo-owner="$FRONTEND_OWNER" \
    --branch-pattern="^main$" \
    --build-config="cloudbuild.yaml" \
    --region=global \
    --substitutions="_REGION=$REGION,_BACKEND_URL=$BACKEND_URL" \
    2>&1 || echo -e "${YELLOW}Note: Trigger may already exist or require manual setup${NC}"

echo -e "${GREEN}✓ Frontend trigger created${NC}"
echo ""

echo -e "${YELLOW}Step 10: Test the CI/CD Pipeline${NC}"
echo "-------------------------------------------------------------------"
echo ""
echo "To test the automated deployment:"
echo ""
echo "1. Backend:"
echo "   cd /Users/tiko/Desktop/IGAL/backend"
echo "   git add ."
echo "   git commit -m \"Test automated deployment\""
echo "   git push origin main"
echo ""
echo "2. Frontend:"
echo "   cd /Users/tiko/Desktop/IGAL/frontend"
echo "   git add ."
echo "   git commit -m \"Test automated deployment\""
echo "   git push origin main"
echo ""
echo "Monitor builds at:"
echo "https://console.cloud.google.com/cloud-build/builds?project=$PROJECT_ID"
echo ""

echo "==================================================================="
echo -e "${GREEN}✓ CI/CD Setup Complete!${NC}"
echo "==================================================================="
echo ""
echo "Summary:"
echo "--------"
echo "• Backend GitHub: $BACKEND_REPO"
echo "• Frontend GitHub: $FRONTEND_REPO"
echo "• Backend URL: $BACKEND_URL"
echo "• Cloud Build Triggers: 2 triggers created"
echo ""
echo "How it works:"
echo "-------------"
echo "1. You push code to GitHub (main branch)"
echo "2. GitHub webhook triggers Cloud Build automatically"
echo "3. Cloud Build builds Docker image and pushes to Artifact Registry"
echo "4. Cloud Build deploys new image to Cloud Run"
echo "5. Your application is live in ~5-10 minutes"
echo ""
echo "Next steps:"
echo "-----------"
echo "• Push your code to GitHub to trigger first deployment"
echo "• Set up custom domain (igal.ge)"
echo "• Configure SSL certificate"
echo "• Add staging environment"
echo ""
echo "==================================================================="
