# 🚀 Quick Start: Deploy to Streamlit Cloud

## ✅ Files Ready for Deployment

Your repository now has everything needed for Streamlit Cloud:
- `streamlit_app.py` - Main application
- `requirements.txt` - Dependencies
- `.streamlit/config.toml` - Configuration
- `.streamlit/secrets.toml.example` - Secrets template
- `STREAMLIT_DEPLOYMENT.md` - Full deployment guide

## 📝 Deploy in 3 Steps

### 1. Go to Streamlit Cloud
Visit: https://share.streamlit.io

### 2. Create New App
- Click "New app"
- Repository: `SarthakRay26/Automation_QA_testing`
- Branch: `main`
- Main file: `streamlit_app.py`

### 3. (Optional) Add Secrets
For GitHub Actions features, click "Advanced settings" and add:
```toml
GITHUB_TOKEN = "ghp_your_github_personal_access_token_here"
GITHUB_USERNAME = "your_github_username"
```

## ⚡ Your App URL
After deployment (2-3 min), you'll get a URL like:
```
https://sarthakray26-automation-qa-testing.streamlit.app
```

## 🎯 What Works on Streamlit Cloud

✅ **Without Backend:**
- Manual test case input (JSON format)
- Selenium script generation
- Script download

✅ **With Backend (Optional):**
- GitHub Actions execution
- Workflow status tracking
- Test result viewing

## 🔧 To Enable GitHub Features

Deploy the Node.js backend separately on Railway:

```bash
cd github-actions-backend
railway login
railway init
railway up
```

Then add to Streamlit secrets:
```toml
GITHUB_BACKEND_URL = "https://your-app.railway.app"
```

## 📖 Full Documentation
See `STREAMLIT_DEPLOYMENT.md` for complete details.

## 🐛 Troubleshooting

**App won't start?**
- Check logs in Streamlit Cloud dashboard
- Verify requirements.txt is valid

**GitHub features not working?**
- Add GITHUB_TOKEN to secrets
- Deploy Node.js backend separately

## 💡 Quick Test

After deployment, try this test case:
```json
{
    "test_id": "TC001",
    "title": "Verify form submission",
    "description": "Test form with all fields",
    "test_steps": [
        "Enter text in coupon-code field",
        "Enter card number in card-number field",
        "Click submit button"
    ]
}
```

Click "Generate Selenium Script" → Script appears → Download it!

---

**Need help?** Check `STREAMLIT_DEPLOYMENT.md` for detailed instructions.
