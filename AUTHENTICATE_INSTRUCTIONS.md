# How to Authenticate info@igal.ge

## The authentication URL is opening in Chrome now.

## Steps to Complete Authentication:

### Option 1: Use Terminal (Recommended)

Open a **new Terminal window** and run:

```bash
gcloud auth login info@igal.ge
```

This will:
1. Open a browser window
2. Ask you to sign in with `info@igal.ge`
3. Show a verification code
4. Paste the code back in the terminal
5. Complete authentication

### Option 2: Manual Process

If the command above doesn't work:

1. **In the Chrome window that just opened**:
   - Sign in with `info@igal.ge`
   - Accept the permissions
   - Copy the verification code shown

2. **In your terminal**, run:
   ```bash
   gcloud config set account info@igal.ge
   gcloud config set project igal-ai-project
   ```

3. Then verify authentication worked:
   ```bash
   gcloud auth list
   ```

   You should see `info@igal.ge` with an asterisk (*) next to it.

---

## After Authentication is Complete:

Run this command to fix the organization policy and enable production access:

```bash
bash /Users/tiko/Desktop/IGAL/fix-org-policy.sh
```

This will:
- ✅ Create organization policy exception
- ✅ Add public access to Cloud Run backend
- ✅ Test production endpoint
- ✅ Enable widget to work on any website

---

## Troubleshooting

**If you get "Permission denied":**
- Make sure you granted Organization Admin role to `info@igal.ge` in Google Cloud Console
- Wait 1-2 minutes for permissions to propagate
- Try running the fix script again

**If gcloud command not found:**
```bash
# Check if gcloud is installed
which gcloud

# If not installed, install Google Cloud SDK:
# https://cloud.google.com/sdk/docs/install
```

**If you're not sure about your permissions:**
```bash
# Check your current account
gcloud config get-value account

# Check your permissions on the organization
gcloud organizations get-iam-policy 123688009790 \
  --flatten="bindings[].members" \
  --filter="bindings.members:info@igal.ge" \
  --format="table(bindings.role)"
```

You should see `roles/resourcemanager.organizationAdmin` in the output.
