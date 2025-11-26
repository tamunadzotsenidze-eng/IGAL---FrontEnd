#!/bin/bash
# Script to grant Organization Admin permissions
# Run this if you have Workspace Super Admin access

# Organization ID for igal.ge
ORG_ID="123688009790"

# Your email
YOUR_EMAIL="tamuna.dzotsenidze@igal.ge"

echo "========================================="
echo "Granting Organization Admin Permissions"
echo "========================================="
echo ""
echo "Organization: igal.ge ($ORG_ID)"
echo "User: $YOUR_EMAIL"
echo ""

# Grant Organization Admin role
echo "Granting roles/resourcemanager.organizationAdmin..."
gcloud organizations add-iam-policy-binding $ORG_ID \
  --member="user:$YOUR_EMAIL" \
  --role="roles/resourcemanager.organizationAdmin"

echo ""
echo "✅ Done! You now have Organization Admin permissions."
echo ""
echo "Now you can fix the organization policy:"
echo "Run: bash /Users/tiko/Desktop/IGAL/fix-org-policy.sh"
