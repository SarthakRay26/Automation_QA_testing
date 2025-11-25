# Deploy FastAPI Backend to Heroku

## 🚀 Quick Deployment Steps

### Prerequisites
- Heroku account
- Heroku CLI installed

### Step 1: Check Requirements File

Make sure `qa_agent/requirements.txt` has all dependencies.

### Step 2: Navigate to Backend Directory

```bash
cd /Users/sarthakray/Autonomous_QA_Automation/qa_agent/backend
```

### Step 3: Initialize Git (if needed)

```bash
# Check if already a git repo
git remote -v

# If not, initialize
git init
git add .
git commit -m "Initial FastAPI backend"
```

### Step 4: Create Heroku App

```bash
heroku create qa-fastapi-backend
```

Or use an existing app:
```bash
heroku git:remote -a your-existing-app-name
```

### Step 5: Set Environment Variables

```bash
heroku config:set PYTHONUNBUFFERED=1
```

### Step 6: Deploy

**Option A: Deploy from subdirectory (recommended)**

From main repo root:
```bash
cd /Users/sarthakray/Autonomous_QA_Automation
git subtree push --prefix qa_agent/backend heroku main
```

**Option B: Create separate repo**

If you want a separate repo:
```bash
cd qa_agent/backend
git init
heroku git:remote -a qa-fastapi-backend
git add .
git commit -m "FastAPI backend"
git push heroku main
```

### Step 7: Wait for Build

This will take 5-10 minutes due to heavy ML dependencies (torch, transformers, chromadb).

### Step 8: Scale Up Dyno

**⚠️ IMPORTANT**: Free tier likely won't work due to memory requirements.

```bash
# Check current dyno
heroku ps

# Scale to hobby ($7/mo) or standard
heroku ps:scale web=1:hobby
```

Or upgrade in Heroku dashboard: Resources → Change Dyno Type

---

## ✅ Verify Deployment

```bash
# Check logs
heroku logs --tail

# Test health endpoint
curl https://your-app.herokuapp.com/health
```

Expected response:
```json
{
  "status": "healthy",
  "rag_pipeline": "not initialized",
  "documents_loaded": 0,
  "html_loaded": false,
  "test_cases_generated": 0
}
```

---

## 📊 Heroku Dyno Recommendations

| Dyno Type | RAM | Cost | Suitable? |
|-----------|-----|------|-----------|
| **Free** (Eco) | 512 MB | $0 | ❌ Too small for ML models |
| **Hobby** | 512 MB | $7/mo | ⚠️ Tight but may work |
| **Standard-1X** | 512 MB | $25/mo | ⚠️ Same RAM, more CPU |
| **Standard-2X** | 1 GB | $50/mo | ✅ Recommended |

**Recommendation**: Start with Hobby, upgrade to Standard-2X if crashes occur.

---

## ⚠️ Important Notes

### Memory Issues
If you see crashes like:
```
Error R14 (Memory quota exceeded)
Process running mem=512M(100.0%)
```

**Solutions**:
1. Upgrade dyno type
2. Reduce model size
3. Use lightweight embeddings
4. Switch to API-based models (OpenAI)

### Build Pack
Heroku auto-detects Python. If issues occur:
```bash
heroku buildpacks:set heroku/python
```

### Timeout Issues
ML model loading takes time. Increase boot timeout:
```bash
heroku config:set WEB_CONCURRENCY=1
```

---

## 🔧 After Deployment

### Get Your Heroku URL

```bash
heroku apps:info
```

You'll get: `https://qa-fastapi-backend-xyz.herokuapp.com`

### Update Streamlit Secrets

Add to Streamlit Cloud:
```toml
FASTAPI_BACKEND_URL = "https://qa-fastapi-backend-xyz.herokuapp.com"
GITHUB_BACKEND_URL = "https://automatic-qa-test-9d45ce9dd223.herokuapp.com"
GITHUB_TOKEN = "ghp_your_token"
GITHUB_USERNAME = "SarthakRay26"
```

---

## 🐛 Troubleshooting

### Build Fails
**Check requirements.txt is in backend folder**
```bash
ls qa_agent/backend/requirements.txt
```

### App Crashes Immediately
**Check logs:**
```bash
heroku logs --tail
```

Common issues:
- Out of memory → Upgrade dyno
- Missing dependencies → Check requirements.txt
- Port binding → Already handled in main.py

### Can't Push to Heroku
**Make sure remote is set:**
```bash
heroku git:remote -a your-app-name
```

---

## 💰 Cost Breakdown

**Minimum for FastAPI with ML models**: ~$7-25/month
- Hobby dyno: $7/mo (may crash under load)
- Standard-2X: $50/mo (reliable)

**Free Alternative**: 
- Remove ML dependencies
- Use OpenAI API for embeddings
- Deploy to Railway/Fly.io free tier

---

## 🚀 Deploy Now

```bash
cd /Users/sarthakray/Autonomous_QA_Automation/qa_agent/backend
heroku create qa-fastapi-backend
git add .
git commit -m "Add Heroku deployment config"
git push heroku main
heroku ps:scale web=1:hobby
heroku open
```

**Ready to deploy? Run the commands above!**
