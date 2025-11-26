#!/bin/bash
# Complete authentication for info@igal.ge

echo "========================================="
echo "Completing Authentication"
echo "========================================="
echo ""

# The verification code from Google
VERIFICATION_CODE="4/0Ab32j93QP96aGtOU1zQ6I31jlvsX8LL99WmDy0M3-s1_ywRRJ_Ky44VKzYChE6GOP2u4Fg"

echo "Step 1: Authenticate with info@igal.ge"
echo ""
echo "Please run this command in a new terminal:"
echo ""
echo "gcloud auth login info@igal.ge"
echo ""
echo "When prompted, paste this verification code:"
echo "$VERIFICATION_CODE"
echo ""
echo "========================================="
echo ""
echo "After authentication completes, verify with:"
echo "gcloud auth list"
echo ""
echo "Then run:"
echo "bash /Users/tiko/Desktop/IGAL/fix-org-policy.sh"
echo ""
