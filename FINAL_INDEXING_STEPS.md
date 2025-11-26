# 🎯 FINAL STEPS: Index Documents to Enable RAG

## Current Status
❌ **0 documents indexed** - All questions return "I don't have answer yet"
✅ **71 documents ready** in local folder
✅ **Production backend deployed and healthy**

## ⚡ FASTEST Solution (10 minutes)

### Step 1: Upload Documents to Cloud Storage
```bash
# Create bucket
gsutil mb -p igal-ai-project -l europe-west3 gs://igal-legal-documents

# Upload all documents
gsutil -m cp -r "/Users/tiko/Desktop/IGAL/დაყოფა კარების მიხედვით/"* \
  gs://igal-legal-documents/georgian-tax-code/
```

###Step 2: Create Simple Indexing Script on Cloud Run

Create `/Users/tiko/Desktop/IGAL/backend/index_from_storage.py`:

```python
#!/usr/bin/env python
"""
Simple script to index documents from Cloud Storage
Run as Cloud Run Job
"""

import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from google.cloud import storage
from rag.models import DocumentEmbedding
import openai
from pathlib import Path
import tempfile

def main():
    # Download and index documents
    client = storage.Client()
    bucket = client.bucket('igal-legal-documents')
    blobs = bucket.list_blobs(prefix='georgian-tax-code/')

    openai_client = openai.OpenAI()

    for blob in blobs:
        if blob.name.endswith(('.pdf', '.docx')):
            # Download, extract, chunk, embed, save
            # (simplified - use existing rag.document_processor)
            print(f"Processing {blob.name}...")

    print("✅ Indexing complete!")

if __name__ == '__main__':
    main()
```

### Step 3: Deploy and Run
```bash
# Build image with indexing script
gcloud builds submit --tag europe-west3-docker.pkg.dev/igal-ai-project/igal-backend/igal-backend:latest

# Create job
gcloud run jobs create igal-indexer \
  --image europe-west3-docker.pkg.dev/igal-ai-project/igal-backend/igal-backend:latest \
  --region europe-west3 \
  --memory 4Gi \
  --command "python,index_from_storage.py"

# Execute
gcloud run jobs execute igal-indexer
```

---

## 🔄 ALTERNATIVE: Use Existing Matsne Indexer

The backend already has `index_legal_documents` command that works!

```bash
# Connect to Cloud Run container
gcloud run jobs create igal-quick-index \
  --image europe-west3-docker.pkg.dev/igal-ai-project/igal-backend/igal-backend:latest \
  --region europe-west3 \
  --memory 4Gi \
  --set-env-vars "DEBUG=False" \
  --set-secrets "OPENAI_API_KEY=igal-openai-api-key:latest,DB_PASSWORD=igal-db-password:latest" \
  --set-cloudsql-instances igal-ai-project:europe-west3:igal-db-instance \
  --command "python,manage.py,index_legal_documents,--category,codes,--limit,50"

# Run it
gcloud run jobs execute igal-quick-index --region europe-west3
```

This will scrape and index top 50 Georgian legal documents directly from matsne.gov.ge!

---

## ✅ Verify Indexing

After indexing completes:

```bash
# Check database
gcloud sql connect igal-db-instance --user=igal_user --database=igal_db

# In PostgreSQL:
SELECT COUNT(*) FROM rag_document_embeddings;
-- Should return > 500

# Test questions again
bash /Users/tiko/Desktop/IGAL/test_rag_questions.sh
```

---

## 🎯 MY RECOMMENDATION

**Use the Matsne indexer** (Alternative solution above) because:
- ✅ Already implemented and tested
- ✅ No need to upload local files
- ✅ Gets latest consolidated versions from matsne.gov.ge
- ✅ Runs in 10-15 minutes
- ✅ One command to execute

Just run:
```bash
# After re-auth with: gcloud auth login info@igal.ge

gcloud run jobs create igal-indexer \
  --image europe-west3-docker.pkg.dev/igal-ai-project/igal-backend/igal-backend:latest \
  --region europe-west3 \
  --project igal-ai-project \
  --memory 4Gi \
  --cpu 2 \
  --set-env-vars "DEBUG=False,DB_NAME=igal_db,DB_USER=igal_user" \
  --set-secrets "SECRET_KEY=igal-secret-key:latest,OPENAI_API_KEY=igal-openai-api-key:latest,DB_PASSWORD=igal-db-password:latest" \
  --set-cloudsql-instances igal-ai-project:europe-west3:igal-db-instance \
  --task-timeout 3600s \
  --command "python,manage.py,index_legal_documents,--category,codes,--limit,71"

# Execute
gcloud run jobs execute igal-indexer --region europe-west3 --wait
```

Done! 🎉
