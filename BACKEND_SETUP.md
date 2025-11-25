# Backend Setup Guide

## Overview

Your application uses **TWO separate backends**:

1. **FastAPI Backend** - Handles RAG, document processing, test generation
2. **Node.js Backend (GitHub Actions)** - Handles test execution on GitHub Actions

## Backend Configuration

### 1. FastAPI Backend (qa_agent/backend/main.py)

**Endpoints:**
- `/health` - Health check
- `/upload_documents` - Upload documentation files
- `/upload_html` - Upload HTML files
- `/build_knowledge_base` - Build vector DB
- `/generate_test_cases` - Generate test cases using RAG
- `/generate_selenium_script` - Generate Selenium scripts
- `/test_cases` - Get all test cases
- `/reset` - Reset system

**To run locally:**
```bash
cd qa_agent
python -m backend.main
```

**Default URL:** `http://localhost:8000`

### 2. GitHub Actions Backend (github-actions-backend/src/server.js)

**Endpoints:**
- `/health` - Health check
- `/api/create-test-run` - Create test run on GitHub Actions
- `/api/status/:runId` - Get test run status
- `/api/logs/:runId` - Get test run logs
- `/api/artifacts/:runId` - Get test artifacts

**To run locally:**
```bash
cd github-actions-backend
npm install
node src/server.js
```

**Default URL:** `http://localhost:5000`

**Deployed URL:** `https://automatic-qa-test-9d45ce9dd223.herokuapp.com`

## Streamlit Configuration

The Streamlit app now uses environment variables to configure backend URLs:

### Environment Variables

```bash
# FastAPI Backend URL (for document processing & test generation)
export FASTAPI_BASE_URL="http://localhost:8000"

# GitHub Actions Backend URL (for test execution)
export GITHUB_ACTIONS_BASE_URL="https://automatic-qa-test-9d45ce9dd223.herokuapp.com"
```

### For Streamlit Cloud Deployment

Add these secrets in your Streamlit Cloud dashboard:

1. Go to your app settings
2. Navigate to "Secrets" section
3. Add:

```toml
FASTAPI_BASE_URL = "https://your-fastapi-deployment.herokuapp.com"
GITHUB_ACTIONS_BASE_URL = "https://automatic-qa-test-9d45ce9dd223.herokuapp.com"
```

## Testing the Backends

### Test FastAPI Backend:
```bash
curl http://localhost:8000/health
```

### Test GitHub Actions Backend:
```bash
curl https://automatic-qa-test-9d45ce9dd223.herokuapp.com/health
```

### Test Create Test Run:
```bash
curl -X POST "https://automatic-qa-test-9d45ce9dd223.herokuapp.com/api/create-test-run" \
  -H "Content-Type: application/json" \
  -d '{"testScript": "print(\"Hello\")", "testName": "test_sample"}'
```

## Current Status

✅ **GitHub Actions Backend**: Deployed and working on Heroku
❌ **FastAPI Backend**: Not deployed (runs locally only)

## Next Steps

To make the app fully functional on Streamlit Cloud:

1. **Deploy FastAPI Backend** to a hosting service:
   - Heroku
   - Render
   - Railway
   - Google Cloud Run
   - AWS Lambda

2. **Update Streamlit Secrets** with the deployed FastAPI URL

3. **Test the full flow** on Streamlit Cloud

## Local Development

For local development, both backends should be running:

**Terminal 1 - FastAPI:**
```bash
cd qa_agent
python -m backend.main
```

**Terminal 2 - Node.js:**
```bash
cd github-actions-backend
node src/server.js
```

**Terminal 3 - Streamlit:**
```bash
cd qa_agent/frontend
streamlit run app.py
```

## API Flow

```
Streamlit App
    ├── FastAPI Backend (localhost:8000)
    │   ├── Upload Documents
    │   ├── Build Knowledge Base
    │   ├── Generate Test Cases
    │   └── Generate Selenium Scripts
    │
    └── GitHub Actions Backend (Heroku)
        ├── Create Test Run
        ├── Get Status
        ├── Get Logs
        └── Get Artifacts
```
