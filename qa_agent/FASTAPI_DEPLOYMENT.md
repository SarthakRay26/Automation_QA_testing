# Deploy FastAPI Backend to Render

## 🚀 Quick Deployment Steps

### Step 1: Go to Render
Visit: https://dashboard.render.com

### Step 2: Create New Web Service

1. Click **"New +"** → **"Web Service"**
2. Connect repository: **`SarthakRay26/Automation_QA_testing`**
3. Configure:

| Setting | Value |
|---------|-------|
| **Name** | `qa-fastapi-backend` |
| **Region** | Choose closest to you |
| **Branch** | `main` |
| **Root Directory** | `qa_agent/backend` |
| **Runtime** | `Python 3` |
| **Build Command** | `pip install -r ../requirements.txt` |
| **Start Command** | `uvicorn main:app --host 0.0.0.0 --port $PORT` |
| **Instance Type** | **Starter ($7/mo)** - Free tier insufficient |

### Step 3: Add Environment Variables

```
PYTHONUNBUFFERED = 1
PORT = 8000
```

### Step 4: Add Persistent Disk (Optional but Recommended)

For ChromaDB storage:
- **Mount Path**: `/opt/render/project/src/chroma_db`
- **Size**: 1 GB

### Step 5: Deploy

Click **"Create Web Service"**  
Wait 5-10 minutes (ML dependencies are large)

### Step 6: Get Your URL

You'll get: `https://qa-fastapi-backend-xyz.onrender.com`

---

## ⚠️ Important Notes

### Cost Warning
- **Free tier won't work** - insufficient RAM for ML models
- **Starter plan required**: $7/month minimum
- Models require ~1.5GB RAM minimum

### Build Time
- First deployment: 8-12 minutes
- Heavy dependencies (torch, transformers, chromadb)
- Subsequent deploys: 3-5 minutes

---

## ✅ Verify Deployment

Test health endpoint:
```bash
curl https://your-app.onrender.com/health
```

Should return:
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

## 🔧 After Deployment

### Update Streamlit Secrets

Add to Streamlit Cloud:
```toml
FASTAPI_BACKEND_URL = "https://qa-fastapi-backend-xyz.onrender.com"
GITHUB_BACKEND_URL = "https://automatic-qa-test-9d45ce9dd223.herokuapp.com"
GITHUB_TOKEN = "ghp_your_token"
GITHUB_USERNAME = "SarthakRay26"
```

---

## 📊 Expected Performance

### Cold Start (Free Tier)
- ⚠️ Won't work - insufficient memory

### Starter Plan ($7/mo)
- ✅ Always on
- ✅ 512 MB RAM (barely enough)
- ✅ No cold starts
- ⚠️ May need Standard ($25/mo) for better performance

### Standard Plan ($25/mo)
- ✅ 2 GB RAM (comfortable)
- ✅ Fast model loading
- ✅ Multiple concurrent requests

---

## 🐛 Troubleshooting

### "Build failed" - Out of Memory
**Solution**: Upgrade to Starter or Standard plan

### "Service crashed" after start
**Solution**: Check logs, may need more RAM

### Slow response times
**Solution**: Models loading on first request, consider Standard plan

---

## 💡 Alternative: Lighter Deployment

If cost is an issue, you can:
1. Remove heavy ML dependencies
2. Use simpler embedding models
3. Use OpenAI API instead of local models
4. Deploy to Railway/Fly.io with better free tiers

---

## 📝 Next Steps

After successful deployment:
1. Test all endpoints
2. Update streamlit_app.py to call FastAPI
3. Add document upload feature
4. Test end-to-end workflow

**Ready to deploy?** Follow the steps above!
