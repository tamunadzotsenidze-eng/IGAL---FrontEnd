#!/bin/bash
# Authenticate info@igal.ge and fix organization policy

echo "========================================="
echo "IGAL Production Deployment Setup"
echo "========================================="
echo ""

# Step 1: Authenticate
echo "Step 1: Authenticating info@igal.ge..."
echo ""
echo "Opening browser for authentication..."
gcloud auth login info@igal.ge

# Check if authentication succeeded
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Authentication successful!"
    echo ""

    # Step 2: Set as active account
    echo "Step 2: Setting info@igal.ge as active account..."
    gcloud config set account info@igal.ge
    gcloud config set project igal-ai-project

    # Step 3: Verify permissions
    echo ""
    echo "Step 3: Verifying Organization Admin permissions..."
    gcloud organizations get-iam-policy 123688009790 \
      --flatten="bindings[].members" \
      --filter="bindings.members:info@igal.ge" \
      --format="table(bindings.role)"

    if [ $? -eq 0 ]; then
        echo ""
        echo "✅ You have organization access!"
        echo ""
        echo "Step 4: Ready to fix organization policy?"
        read -p "Press Enter to run fix-org-policy.sh or Ctrl+C to cancel..."

        # Run the fix script
        bash /Users/tiko/Desktop/IGAL/fix-org-policy.sh
    else
        echo ""
        echo "❌ Cannot access organization. You may need to:"
        echo "  1. Wait a few minutes for permissions to propagate"
        echo "  2. Verify you added Organization Admin role correctly"
        echo "  3. Contact your Google Workspace admin"
    fi
else
    echo ""
    echo "❌ Authentication failed"
    echo "Please try again or contact support"
fi
