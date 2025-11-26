# How to Get Organization Admin Permissions

## Current Situation
- **Email**: `tamuna.dzotsenidze@igal.ge`
- **Organization**: `igal.ge` (ID: 123688009790)
- **Current Roles**: Project Owner (on igal-ai-project)
- **Missing**: Organization Administrator role

## Why You Need This
The organization policy `iam.allowedPolicyMemberDomains` is blocking public access to your Cloud Run backend. You need Organization Admin to create a policy exception.

---

## Method 1: GCP IAM Admin Console (FASTEST - Try This First!)

### Steps:
1. **Open**: https://console.cloud.google.com/iam-admin/iam?organizationId=123688009790

2. **If you can access the page**:
   - Click **"+ GRANT ACCESS"** button
   - New principals: `tamuna.dzotsenidze@igal.ge`
   - Select role: **"Organization Administrator"**
   - Click **"SAVE"**
   - ✅ Done! Skip to "After Getting Admin Access" section

3. **If you get permission error**:
   - Continue to Method 2 below

---

## Method 2: Google Workspace Admin Console

### Requirements:
- You need **Super Admin** role in Google Workspace for `igal.ge` domain
- Or ask someone who has Super Admin access

### Steps:
1. **Open Google Workspace Admin Console**:
   ```
   https://admin.google.com
   ```

2. **Navigate to Admin Roles**:
   - Click **"Account"** in the left sidebar
   - Click **"Admin roles"**

3. **Find Organization Administrator**:
   - Look for **"Organization Administrator"** in the list
   - Click on it

4. **Assign the Role**:
   - Click **"Assign users"** or **"Assign service accounts"**
   - Add: `tamuna.dzotsenidze@igal.ge`
   - Click **"Assign"**

5. **Verify**:
   - Wait 1-2 minutes for propagation
   - Run: `gcloud organizations get-iam-policy 123688009790 | grep tamuna`

---

## Method 3: Ask Another Administrator

If you don't have Workspace Super Admin access, ask someone who does:

### They need to run:
```bash
gcloud organizations add-iam-policy-binding 123688009790 \
  --member="user:tamuna.dzotsenidze@igal.ge" \
  --role="roles/resourcemanager.organizationAdmin"
```

---

## Method 4: Via Billing Account Admin (Alternative)

If you have Billing Account Admin role:

1. **Open Billing Console**:
   ```
   https://console.cloud.google.com/billing
   ```

2. **Find your billing account** linked to the organization

3. **Go to IAM tab**:
   - You might be able to grant Organization Admin from there

---

## After Getting Admin Access

Once you have Organization Admin role, run:

```bash
bash /Users/tiko/Desktop/IGAL/fix-org-policy.sh
```

This will:
1. ✅ Create organization policy exception for `igal-ai-project`
2. ✅ Add public access (`allUsers`) to Cloud Run backend
3. ✅ Test backend connectivity
4. ✅ Enable your widget to work in production!

---

## Verification

Check if you have Organization Admin:

```bash
gcloud organizations get-iam-policy 123688009790 \
  --flatten="bindings[].members" \
  --filter="bindings.members:tamuna.dzotsenidze@igal.ge" \
  --format="table(bindings.role)"
```

You should see:
```
roles/resourcemanager.organizationAdmin
```

---

## Need Help?

**If all methods fail**, it means:
- You're not a Workspace Super Admin
- No Organization Admin exists yet
- You need to contact Google Workspace support to set up initial admin

**Common Issues**:
- "Permission denied" = Not a Super Admin
- "Organization not found" = Wrong organization ID
- "Invalid member" = Email not in organization

**Quick Check - Your Current Permissions**:
```bash
# Check project permissions (you have these):
gcloud projects get-iam-policy igal-ai-project \
  --flatten="bindings[].members" \
  --filter="bindings.members:tamuna.dzotsenidze@igal.ge" \
  --format="table(bindings.role)"
```

Current project roles:
- ✅ `roles/owner` - You have this
- ✅ `roles/accesscontextmanager.policyAdmin` - You have this
- ❌ `roles/resourcemanager.organizationAdmin` - You need this
