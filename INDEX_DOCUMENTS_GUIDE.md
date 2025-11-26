# How to Index Legal Documents for RAG System

## Current Status
❌ **0 documents indexed** - RAG system has no data to search
✅ **71 legal documents available** in `/Users/tiko/Desktop/IGAL/დაყოფა კარების მიხედვით/`

## Solution: Index Documents into Production Database

### Option 1: Run Indexing Command Locally (Recommended)

```bash
cd /Users/tiko/Desktop/IGAL/backend

# Set production database connection
export DB_HOST="34.89.185.191"  # Cloud SQL public IP
export DB_NAME="igal_db"
export DB_USER="igal_user"
export DB_PASSWORD="your_password"  # Get from Secret Manager
export OPENAI_API_KEY="your_key"    # For embeddings

# Run indexing command
./venv/bin/python manage.py index_legal_documents \
  --directory "/Users/tiko/Desktop/IGAL/დაყოფა კარების მიხედვით/" \
  --recursive
```

### Option 2: Run Indexing as Cloud Run Job

```bash
gcloud run jobs create igal-indexer \
  --image europe-west3-docker.pkg.dev/igal-ai-project/igal-backend/igal-backend:latest \
  --region europe-west3 \
  --project igal-ai-project \
  --memory 4Gi \
  --cpu 2 \
  --set-env-vars "DEBUG=False,DB_NAME=igal_db,DB_USER=igal_user,RAG_ENABLED=True" \
  --set-secrets "SECRET_KEY=igal-secret-key:latest,OPENAI_API_KEY=igal-openai-api-key:latest,DB_PASSWORD=igal-db-password:latest" \
  --set-cloudsql-instances igal-ai-project:europe-west3:igal-db-instance \
  --task-timeout 3600s \
  --command "python,manage.py,index_igal_documents_complete"
```

### Option 3: Upload Documents to Production and Index

1. **Copy documents to Cloud Storage:**
```bash
gsutil -m cp -r "/Users/tiko/Desktop/IGAL/დაყოფა კარების მიხედვით/" \
  gs://igal-ai-project_documents/legal_docs/
```

2. **Create indexing script:**
```bash
# Run on Cloud Run Job
gcloud run jobs execute igal-indexer --region europe-west3
```

---

## What Gets Indexed

### Document Statistics:
- **Total Documents**: 71 legal documents
- **Document Types**: PDF, DOCX
- **Topics**:
  - საგადასახადო კოდექსი (Tax Code)
  - დღგ (VAT)
  - საშემოსავლო გადასახადი (Income Tax)
  - მოგების გადასახადი (Profit Tax)
  - საბაჟო პროცედურები (Customs)
  - სპეციალური რეჟიმები (Special Regimes)

### Indexing Process:
1. **Extract text** from PDF/DOCX files
2. **Split into chunks** (~500-1000 characters)
3. **Generate embeddings** using OpenAI (text-embedding-3-small)
4. **Store in PostgreSQL** with pgvector
5. **Enable fast similarity search**

---

## Verify Indexing Success

After indexing, check the database:

```bash
# Connect to production database
gcloud sql connect igal-db-instance --user=igal_user --database=igal_db

# Run in PostgreSQL:
SELECT COUNT(*) as total_embeddings FROM rag_document_embeddings;
SELECT COUNT(DISTINCT document_id) as total_documents FROM rag_document_embeddings;

# Should see:
# total_embeddings: ~500-1000 (chunks)
# total_documents: 71
```

---

## Test After Indexing

Run the test script again:

```bash
bash /Users/tiko/Desktop/IGAL/test_rag_questions.sh
```

Expected result:
✅ **Detailed answers** with citations from legal documents

---

## Troubleshooting

### Issue: "ChromaDB not available"
**Solution**: Production uses PostgreSQL with pgvector, not ChromaDB. The code automatically falls back to PostgreSQL vector store.

### Issue: "No OpenAI API key"
**Solution**: Ensure `OPENAI_API_KEY` is set in Cloud Run environment or Secret Manager.

### Issue: "Permission denied"
**Solution**: Ensure Cloud Run service account has Cloud SQL Client role.

---

## Next Steps

1. ✅ Get database password from Secret Manager:
   ```bash
   gcloud secrets versions access latest --secret="igal-db-password"
   ```

2. ✅ Run indexing (Option 1, 2, or 3 above)

3. ✅ Verify documents are indexed (database query)

4. ✅ Test with Georgian questions

5. ✅ Deploy widget with working RAG! 🚀
