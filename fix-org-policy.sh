#!/bin/bash
# Script to fix organization policy after getting admin permissions

ORG_ID="123688009790"

echo "========================================="
echo "Fixing Organization Policy"
echo "========================================="
echo ""

# Create policy exception for igal-ai-project
echo "Creating policy exception for igal-ai-project..."
gcloud org-policies set-policy - << EOF
name: organizations/$ORG_ID/policies/iam.allowedPolicyMemberDomains
spec:
  rules:
    - condition:
        expression: "resource.matchProject('projects/igal-ai-project')"
      allowAll: true
    - enforce: true
EOF

echo ""
echo "✅ Organization policy updated!"
echo ""
echo "Now adding public access to backend..."

# Add public access to Cloud Run backend
gcloud run services add-iam-policy-binding igal-backend \
  --region=europe-west3 \
  --member="allUsers" \
  --role="roles/run.invoker" \
  --project=igal-ai-project

echo ""
echo "✅ Backend is now publicly accessible!"
echo ""
echo "Testing backend..."
curl -s https://igal-backend-qnv4kru4hq-ey.a.run.app/health/ | head -5

echo ""
echo "========================================="
echo "✅ ALL DONE! Backend is live!"
echo "========================================="
