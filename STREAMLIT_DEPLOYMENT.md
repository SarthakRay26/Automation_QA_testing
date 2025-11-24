# Deploying to Streamlit Cloud

This guide will help you deploy the Autonomous QA Agent to Streamlit Cloud.

## 📋 Prerequisites

1. **GitHub Account** - Your code must be in a GitHub repository
2. **Streamlit Cloud Account** - Sign up at [share.streamlit.io](https://share.streamlit.io)
3. **GitHub Personal Access Token** (optional, for GitHub Actions execution)

## 🚀 Quick Deployment Steps

### Step 1: Prepare Your Repository

Your repository should have these files in the root:
```
Autonomous_QA_Automation/
├── streamlit_app.py          # Main Streamlit application
├── requirements.txt           # Python dependencies
├── .streamlit/
│   ├── config.toml           # Streamlit configuration
│   └── secrets.toml.example  # Secrets template
├── .gitignore                # Git ignore rules
└── STREAMLIT_DEPLOYMENT.md   # This file
```

### Step 2: Commit and Push to GitHub

```bash
cd /Users/sarthakray/Autonomous_QA_Automation
git add streamlit_app.py requirements.txt .streamlit/
git commit -m "Add Streamlit Cloud deployment files"
git push origin main
```

### Step 3: Deploy on Streamlit Cloud

1. **Go to Streamlit Cloud**
   - Visit [share.streamlit.io](https://share.streamlit.io)
   - Click "New app"

2. **Connect Your Repository**
   - Repository: `SarthakRay26/Automation_QA_testing`
   - Branch: `main`
   - Main file path: `streamlit_app.py`

3. **Configure Secrets** (Optional - for GitHub Actions)
   - Click "Advanced settings"
   - In the "Secrets" section, paste:
   ```toml
   GITHUB_TOKEN = "ghp_your_personal_access_token"
   GITHUB_USERNAME = "SarthakRay26"
   ```

4. **Deploy**
   - Click "Deploy!"
   - Wait 2-3 minutes for deployment

5. **Access Your App**
   - You'll get a URL like: `https://sarthakray26-automation-qa-testing.streamlit.app`

## 🔧 Architecture for Streamlit Cloud

Since Streamlit Cloud can only host the frontend, here's the recommended architecture:

### Option 1: Simplified (Script Generation Only)
**What works on Streamlit Cloud:**
- ✅ Manual test case input
- ✅ Selenium script generation
- ✅ Script download
- ✅ GitHub Actions integration (if backend is hosted)

**What needs separate hosting:**
- ⚠️ FastAPI backend (RAG pipeline) - Optional
- ⚠️ Node.js backend (GitHub Actions) - Optional

### Option 2: Full Stack (Recommended)

Deploy the backends separately:

1. **Streamlit App** → Streamlit Cloud (FREE)
   - Main UI for script generation
   - Uses: `streamlit_app.py`

2. **Node.js Backend** → Railway/Render/Heroku (FREE tier available)
   - GitHub Actions workflow management
   - Location: `github-actions-backend/`
   - Environment variables needed:
     - `GITHUB_TOKEN`
     - `GITHUB_USERNAME`

3. **FastAPI Backend** → Railway/Render/Heroku (Optional)
   - RAG pipeline for document-based test generation
   - Location: `qa_agent/backend/`

### Deploying Node.js Backend to Railway

If you want GitHub Actions execution features:

1. **Install Railway CLI**
   ```bash
   npm install -g @railway/cli
   ```

2. **Login to Railway**
   ```bash
   railway login
   ```

3. **Deploy Backend**
   ```bash
   cd github-actions-backend
   railway init
   railway up
   ```

4. **Set Environment Variables in Railway**
   ```
   GITHUB_TOKEN=ghp_your_token
   GITHUB_USERNAME=SarthakRay26
   PORT=5000
   ```

5. **Get Your Backend URL**
   - Railway will provide a URL like: `https://github-backend.railway.app`

6. **Update Streamlit Secrets**
   In Streamlit Cloud settings, add:
   ```toml
   GITHUB_BACKEND_URL = "https://github-backend.railway.app"
   GITHUB_TOKEN = "ghp_your_token"
   GITHUB_USERNAME = "SarthakRay26"
   ```

## 🔐 Setting Up GitHub Personal Access Token

To use GitHub Actions execution:

1. Go to GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Generate new token with these scopes:
   - `repo` (Full control of private repositories)
   - `workflow` (Update GitHub Action workflows)
   - `delete_repo` (Delete repositories - for cleanup)
3. Copy the token (starts with `ghp_`)
4. Add it to Streamlit Cloud secrets

## ✅ Testing Your Deployment

After deployment:

1. **Visit Your App URL**
   - Should load without errors

2. **Test Script Generation**
   - Enter a test case in JSON format
   - Click "Generate Selenium Script"
   - Script should appear

3. **Test Download**
   - Click "Download Script"
   - File should download

4. **Test GitHub Execution** (if backend deployed)
   - Configure GitHub credentials
   - Click "Run on GitHub Actions"
   - Check workflow status on GitHub

## 🐛 Troubleshooting

### App Won't Start
- Check requirements.txt has all dependencies
- Check Streamlit Cloud logs for errors
- Verify streamlit_app.py is in the root

### GitHub Actions Not Working
- Verify GITHUB_TOKEN and GITHUB_USERNAME in secrets
- Check Node.js backend is deployed and accessible
- Verify GITHUB_BACKEND_URL is correct

### "Cannot connect to backend" Warning
- This is normal if Node.js backend isn't deployed
- Script generation still works
- Only GitHub execution is disabled

## 📊 Free Tier Limitations

**Streamlit Cloud (Free):**
- 1 GB RAM
- 1 CPU core
- Apps sleep after inactivity (wake up on visit)
- Perfect for demos and small projects

**Railway (Free Tier):**
- $5 credit per month
- Enough for backend hosting
- Apps don't sleep

**Alternative: Render (Free Tier):**
- Apps sleep after 15 min inactivity
- Free tier available
- Good for occasional use

## 🔄 Updating Your App

When you push to GitHub:
```bash
git add .
git commit -m "Update app"
git push origin main
```

Streamlit Cloud will automatically redeploy (takes 1-2 minutes).

## 📝 Best Practices

1. **Use Secrets for Tokens**
   - Never commit tokens to GitHub
   - Always use Streamlit secrets

2. **Test Locally First**
   ```bash
   streamlit run streamlit_app.py
   ```

3. **Monitor Usage**
   - Check Streamlit Cloud analytics
   - Monitor Railway/Render usage

4. **Keep Dependencies Minimal**
   - Only include required packages in requirements.txt
   - Faster deployment and less memory

## 🎯 What You Get

With this deployment:
- ✅ Public URL for your QA Agent
- ✅ Automatic updates from GitHub
- ✅ HTTPS enabled
- ✅ No server management
- ✅ Free hosting (with limitations)

## 🔗 Useful Links

- [Streamlit Cloud Docs](https://docs.streamlit.io/streamlit-community-cloud)
- [Railway Docs](https://docs.railway.app/)
- [Render Docs](https://render.com/docs)
- [GitHub Actions Docs](https://docs.github.com/en/actions)

## 💡 Tips

1. **Start Simple**: Deploy just the Streamlit app first
2. **Add Backends Later**: If you need RAG or GitHub execution
3. **Use Examples**: Test with the provided sample test cases
4. **Share Your URL**: Anyone can access your deployed app

## 🆘 Support

If you encounter issues:
1. Check Streamlit Cloud logs
2. Review GitHub repository settings
3. Verify all secrets are configured
4. Test Node.js backend separately

---

**Ready to deploy?** Follow Step 1 and push your code to GitHub! 🚀
