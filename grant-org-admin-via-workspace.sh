#!/bin/bash
# Grant Organization Admin via Google Cloud (alternative method)
# This assumes you have at least Project Owner role

ORG_ID="123688009790"
PROJECT_ID="igal-ai-project"
YOUR_EMAIL="tamuna.dzotsenidze@igal.ge"

echo "========================================="
echo "Granting Organization Admin (via Project)"
echo "========================================="
echo ""
echo "Organization: igal.ge ($ORG_ID)"
echo "User: $YOUR_EMAIL"
echo ""

# First, let's check your current project-level permissions
echo "Checking your current permissions..."
gcloud projects get-iam-policy $PROJECT_ID \
  --flatten="bindings[].members" \
  --filter="bindings.members:$YOUR_EMAIL" \
  --format="table(bindings.role)"

echo ""
echo "Attempting to grant Organization Admin role..."
echo "(This will fail if you don't have the permission, but we'll try anyway)"
echo ""

# Try to grant the role
gcloud organizations add-iam-policy-binding $ORG_ID \
  --member="user:$YOUR_EMAIL" \
  --role="roles/resourcemanager.organizationAdmin" \
  2>&1 | tee /tmp/grant-result.txt

# Check if it succeeded
if grep -q "Updated IAM policy" /tmp/grant-result.txt; then
    echo ""
    echo "✅ SUCCESS! You now have Organization Admin permissions."
    echo ""
    echo "Next step: Run the fix script"
    echo "bash /Users/tiko/Desktop/IGAL/fix-org-policy.sh"
else
    echo ""
    echo "❌ FAILED: You don't have permission to grant Organization Admin"
    echo ""
    echo "📋 You need to use ONE of these methods:"
    echo ""
    echo "Method 1: Google Workspace Admin Console"
    echo "  1. Go to https://admin.google.com"
    echo "  2. Navigate to: Account → Admin roles"
    echo "  3. Find 'Organization Administrator' role"
    echo "  4. Assign it to: $YOUR_EMAIL"
    echo ""
    echo "Method 2: Contact someone with Organization Admin"
    echo "  Ask them to run: gcloud organizations add-iam-policy-binding $ORG_ID \\"
    echo "    --member='user:$YOUR_EMAIL' \\"
    echo "    --role='roles/resourcemanager.organizationAdmin'"
    echo ""
    echo "Method 3: Use Billing Account Admin"
    echo "  If you have Billing Account Admin role, you can:"
    echo "  1. Go to: https://console.cloud.google.com/iam-admin/iam?organizationId=$ORG_ID"
    echo "  2. Click '+ GRANT ACCESS'"
    echo "  3. Add principal: $YOUR_EMAIL"
    echo "  4. Select role: 'Organization Administrator'"
    echo "  5. Click 'SAVE'"
    echo ""
fi
