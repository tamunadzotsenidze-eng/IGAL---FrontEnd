# Organization Policy Fix Guide - IGAL Project

**Date**: November 18, 2025
**Project**: igal-ai-project
**Organization**: igal.ge (ID: 123688009790)
**Issue**: Organization policy blocking public access to Cloud Run services

---

## Current Situation

### What's Working ✅
- Backend deployed and running on Cloud Run
- Gunicorn started successfully with 2 workers
- Database connected (Cloud SQL PostgreSQL)
- Secrets configured properly
- Docker images building and pushing to Artifact Registry
- CI/CD triggers created for both backend and frontend

### What's Blocked ⚠️
- **Public access to backend returns 403 Forbidden**
- **Organization policy `constraints/iam.allowedPolicyMemberDomains` prevents adding `allUsers`**
- **Frontend cannot access backend**

### Error Details
```
ERROR: (gcloud.run.services.add-iam-policy-binding) FAILED_PRECONDITION:
One or more users named in the policy do not belong to a permitted customer,
perhaps due to an organization policy.
```

---

## Your Permissions

- **Project Role**: Owner (roles/owner) ✅
- **Organization Role**: None ❌
- **What you CAN do**: Manage project resources, deploy services, create triggers
- **What you CANNOT do**: Modify organization policies (requires Organization Admin)

---

## Solution Options

### Option 1: Request Organization Policy Modification (RECOMMENDED)

**Who can do this**: Organization Administrator for igal.ge

**Steps**:
1. Contact your GCP organization administrator (someone with Organization Admin role at igal.ge)
2. Ask them to modify the organization policy to allow `allUsers` for Cloud Run services
3. Provide them with this command to run:

```bash
gcloud org-policies set-policy - << EOF
name: organizations/123688009790/policies/iam.allowedPolicyMemberDomains
spec:
  rules:
    - allowAll: true
EOF
```

**Or** they can create an exception for your specific project:

```bash
gcloud org-policies set-policy - << EOF
name: organizations/123688009790/policies/iam.allowedPolicyMemberDomains
spec:
  rules:
    - condition:
        expression: "resource.matchProject('projects/igal-ai-project')"
      allowAll: true
    - enforce: true
EOF
```

**Time**: 5-10 minutes
**Benefits**: Permanent fix, simplest solution
**Drawbacks**: Requires organization admin access

---

### Option 2: Use Cloud Load Balancer with Serverless NEG (TEMPORARY WORKAROUND)

This option creates a load balancer in front of your Cloud Run service, which can bypass the organization policy restriction.

**Steps**:
1. Reserve a static IP address:
```bash
gcloud compute addresses create igal-backend-ip --global
```

2. Create serverless network endpoint group (NEG):
```bash
gcloud compute network-endpoint-groups create igal-backend-neg \
    --region=europe-west3 \
    --network-endpoint-type=serverless \
    --cloud-run-service=igal-backend
```

3. Create backend service:
```bash
gcloud compute backend-services create igal-backend-lb \
    --global \
    --load-balancing-scheme=EXTERNAL_MANAGED

gcloud compute backend-services add-backend igal-backend-lb \
    --global \
    --network-endpoint-group=igal-backend-neg \
    --network-endpoint-group-region=europe-west3
```

4. Create URL map:
```bash
gcloud compute url-maps create igal-backend-urlmap \
    --default-service=igal-backend-lb
```

5. Create HTTP(S) target proxy and forwarding rule:
```bash
# For HTTPS (recommended):
gcloud compute ssl-certificates create igal-backend-cert \
    --domains=api.igal.ge

gcloud compute target-https-proxies create igal-backend-https-proxy \
    --url-map=igal-backend-urlmap \
    --ssl-certificates=igal-backend-cert

gcloud compute forwarding-rules create igal-backend-https \
    --global \
    --target-https-proxy=igal-backend-https-proxy \
    --address=igal-backend-ip \
    --ports=443

# For HTTP (testing only):
gcloud compute target-http-proxies create igal-backend-http-proxy \
    --url-map=igal-backend-urlmap

gcloud compute forwarding-rules create igal-backend-http \
    --global \
    --target-http-proxy=igal-backend-http-proxy \
    --address=igal-backend-ip \
    --ports=80
```

6. Get your load balancer IP:
```bash
gcloud compute addresses describe igal-backend-ip --global --format='value(address)'
```

**Time**: 20-30 minutes
**Cost**: ~$18-25/month for load balancer
**Benefits**: Works without organization policy change, provides static IP
**Drawbacks**: Additional cost, more complex setup

---

### Option 3: Internal Service Authentication (DEVELOPMENT ONLY)

Use service account authentication for frontend to access backend.

**Steps**:
1. Create a service account for frontend:
```bash
gcloud iam service-accounts create igal-frontend-sa \
    --display-name="IGAL Frontend Service Account"
```

2. Grant frontend service account permission to invoke backend:
```bash
gcloud run services add-iam-policy-binding igal-backend \
    --region=europe-west3 \
    --member="serviceAccount:igal-frontend-sa@igal-ai-project.iam.gserviceaccount.com" \
    --role="roles/run.invoker"
```

3. Update frontend Cloud Run service to use this service account:
```bash
gcloud run services update igal-frontend \
    --region=europe-west3 \
    --service-account=igal-frontend-sa@igal-ai-project.iam.gserviceaccount.com
```

4. Modify frontend code to include authentication token when calling backend:
```javascript
// In frontend API calls
const auth = new GoogleAuth();
const client = await auth.getIdTokenClient(backendUrl);
const response = await client.request({
  url: backendUrl,
  method: 'GET',
});
```

**Time**: 30-45 minutes (requires code changes)
**Benefits**: Secure, no organization policy needed
**Drawbacks**: Frontend must be deployed on Cloud Run, users cannot access backend directly, requires code modifications

---

### Option 4: Deploy Backend with Ingress Restrictions (NOT RECOMMENDED FOR PUBLIC APP)

Restrict backend to internal traffic only, then use VPC connector.

```bash
gcloud run services update igal-backend \
    --region=europe-west3 \
    --ingress=internal
```

**Benefits**: Very secure
**Drawbacks**: Requires VPC setup, frontend must be in same VPC, complex networking

---

## Recommended Action Plan

### For Production (Choose ONE):

**If you can contact organization admin** → Use **Option 1** (5-10 minutes)

**If you cannot get org admin help** → Use **Option 2** (Load Balancer) (20-30 minutes)

---

## Step-by-Step: Option 1 (Contact Organization Admin)

1. **Find your organization administrator**:
   - They likely have `@igal.ge` email
   - Check Google Workspace admin console
   - Or run: `gcloud organizations get-iam-policy 123688009790` (from their account)

2. **Send them this message**:
   ```
   Hi,

   I need to enable public access to our Cloud Run services in the igal-ai-project.
   Our services are currently blocked by the organization policy "iam.allowedPolicyMemberDomains".

   Could you please run this command to create an exception for our project?

   gcloud org-policies set-policy - << EOF
   name: organizations/123688009790/policies/iam.allowedPolicyMemberDomains
   spec:
     rules:
       - condition:
           expression: "resource.matchProject('projects/igal-ai-project')"
         allowAll: true
       - enforce: true
   EOF

   This will allow allUsers access only for our specific project while keeping
   the organization-wide restriction in place for other projects.

   Thanks!
   ```

3. **After they run the command, test it**:
```bash
# Add public access (should now work)
gcloud run services add-iam-policy-binding igal-backend \
    --region=europe-west3 \
    --member="allUsers" \
    --role="roles/run.invoker"

# Test the endpoint
curl https://igal-backend-qnv4kru4hq-ey.a.run.app/health/
```

4. **If successful, you should see**:
```json
{"status": "healthy", "timestamp": "..."}
```

---

## After Policy Fix: Complete Deployment

Once the organization policy is fixed:

### 1. Update Frontend Trigger
```bash
# Open Cloud Build Triggers console
open "https://console.cloud.google.com/cloud-build/triggers/edit/38643084-25d5-45c6-a4d3-224d0311ae98?project=igal-ai-project&authuser=8"

# Update the substitution variable:
# _BACKEND_URL: https://igal-backend-qnv4kru4hq-ey.a.run.app
```

### 2. Run Database Migrations
```bash
# From your local machine or Cloud Shell
cd /Users/tiko/Desktop/IGAL/backend

# Run migrations via Cloud Run job (one-time)
gcloud run jobs create igal-migrate \
    --image=europe-west3-docker.pkg.dev/igal-ai-project/igal-backend-repo/igal-backend:latest \
    --region=europe-west3 \
    --set-env-vars="DEBUG=False,DB_NAME=igal_db,DB_USER=igal_user" \
    --set-secrets="SECRET_KEY=igal-secret-key:latest,OPENAI_API_KEY=igal-openai-api-key:latest,DB_PASSWORD=igal-db-password:latest" \
    --set-cloudsql-instances=igal-ai-project:europe-west3:igal-db-instance \
    --tasks=1 \
    --max-retries=0 \
    --command=python \
    --args="manage.py,migrate"

# Execute the migration job
gcloud run jobs execute igal-migrate --region=europe-west3 --wait
```

### 3. Test CI/CD Pipeline
```bash
# Backend
cd /Users/tiko/Desktop/IGAL/backend
git add .
git commit -m "Fix: Remove migration step from cloudbuild.yaml"
git push origin main

# Watch the build
open "https://console.cloud.google.com/cloud-build/builds?project=igal-ai-project&authuser=8"
```

### 4. Deploy Frontend
```bash
cd /Users/tiko/Desktop/IGAL/frontend
git add .
git commit -m "Update backend URL to new Cloud Run service"
git push origin main
```

---

## Monitoring and Verification

### Check Backend Status
```bash
# Get service details
gcloud run services describe igal-backend --region=europe-west3

# Check logs
gcloud run services logs read igal-backend --region=europe-west3 --limit=50

# Test health endpoint
curl https://igal-backend-qnv4kru4hq-ey.a.run.app/health/
```

### Monitor CI/CD Builds
```bash
# List recent builds
gcloud builds list --limit=10

# View specific build logs
gcloud builds log BUILD_ID
```

---

## Current Backend Details

- **Service Name**: igal-backend
- **Current URL**: https://igal-backend-qnv4kru4hq-ey.a.run.app
- **Region**: europe-west3 (Frankfurt)
- **Status**: RUNNING (Gunicorn active with 2 workers)
- **Latest Revision**: igal-backend-00002-lt9
- **Issue**: 403 Forbidden due to organization policy
- **Database**: Connected to Cloud SQL (igal-ai-project:europe-west3:igal-db-instance)

---

## Summary

**Problem**: Organization policy `constraints/iam.allowedPolicyMemberDomains` blocks public access

**Root Cause**: You don't have Organization Admin permissions

**Best Solution**: Contact organization admin to create policy exception (Option 1)

**Alternative**: Use Cloud Load Balancer (Option 2) if org admin unavailable

**Next Steps**: Choose and implement one of the solutions above, then complete the deployment

---

**Created**: November 18, 2025
**Last Updated**: November 18, 2025
**Status**: Waiting for organization policy fix or workaround implementation
