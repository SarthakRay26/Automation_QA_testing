# Deploying Node.js Backend to Render

This guide will help you deploy the GitHub Actions backend to Render.

## 🎯 Two Options

### Option 1: Deploy from Subdirectory (Recommended - Same Repo)
Render can deploy from the `github-actions-backend/` folder in your existing repo.

### Option 2: Create Separate Repository
Create a new repo with just the backend code.

---

## 📋 Option 1: Deploy from Subdirectory (Easiest)

### Step 1: Create `render.yaml` Configuration

We'll create a `render.yaml` file in your backend directory.

### Step 2: Sign Up for Render

1. Go to https://render.com
2. Sign up with GitHub
3. Authorize Render to access your repositories

### Step 3: Create New Web Service

1. Click "New +" → "Web Service"
2. Connect your repository: `SarthakRay26/Automation_QA_testing`
3. Configure:
   - **Name**: `github-actions-backend` (or any name)
   - **Region**: Choose closest to you
   - **Branch**: `main`
   - **Root Directory**: `github-actions-backend`
   - **Runtime**: `Node`
   - **Build Command**: `npm install`
   - **Start Command**: `npm start`
   - **Instance Type**: `Free` (or paid for better performance)

### Step 4: Add Environment Variables

In Render dashboard, add these environment variables:
```
GITHUB_TOKEN=ghp_your_personal_access_token
GITHUB_USERNAME=SarthakRay26
NODE_ENV=production
PORT=5000
```

### Step 5: Deploy

- Click "Create Web Service"
- Wait 3-5 minutes for deployment
- You'll get a URL like: `https://github-actions-backend.onrender.com`

### Step 6: Update Streamlit Secrets

In Streamlit Cloud, add:
```toml
GITHUB_BACKEND_URL = "https://github-actions-backend.onrender.com"
```

---

## 📋 Option 2: Deploy from Separate Repository

If you prefer a separate repo:

### Step 1: Create New Repository

```bash
# Create new directory
mkdir github-actions-backend-deploy
cd github-actions-backend-deploy

# Copy backend files
cp -r /Users/sarthakray/Autonomous_QA_Automation/github-actions-backend/* .

# Initialize git
git init
git add .
git commit -m "Initial commit"

# Create GitHub repo and push
gh repo create github-actions-backend --public --source=. --remote=origin --push
```

### Step 2: Deploy to Render

Same as Option 1, but:
- Root Directory: `.` (root)
- Everything else stays the same

---

## 🔧 render.yaml Configuration (Optional)

Create `github-actions-backend/render.yaml`:

```yaml
services:
  - type: web
    name: github-actions-backend
    runtime: node
    plan: free
    buildCommand: npm install
    startCommand: npm start
    envVars:
      - key: NODE_ENV
        value: production
      - key: PORT
        value: 5000
      - key: GITHUB_TOKEN
        sync: false
      - key: GITHUB_USERNAME
        sync: false
```

**Note:** `sync: false` means you'll add these values manually in Render dashboard.

---

## 🚀 Quick Deployment Steps

### For Subdirectory Deployment:

1. **Go to Render**: https://dashboard.render.com
2. **New Web Service** → Connect GitHub
3. **Select Repository**: `Automation_QA_testing`
4. **Configure**:
   ```
   Name: github-actions-backend
   Root Directory: github-actions-backend
   Build Command: npm install
   Start Command: npm start
   ```
5. **Add Environment Variables**:
   - `GITHUB_TOKEN`
   - `GITHUB_USERNAME`
   - `NODE_ENV=production`
6. **Create Web Service**

---

## ⚙️ Environment Variables Needed

| Variable | Value | Description |
|----------|-------|-------------|
| `GITHUB_TOKEN` | `ghp_your_token` | GitHub Personal Access Token |
| `GITHUB_USERNAME` | `SarthakRay26` | Your GitHub username |
| `NODE_ENV` | `production` | Environment mode |
| `PORT` | `5000` | Server port (optional) |

---

## 🔐 Getting GitHub Token

1. GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Generate new token with scopes:
   - ✅ `repo` (Full control)
   - ✅ `workflow` (Update workflows)
   - ✅ `delete_repo` (Delete repos for cleanup)
3. Copy token (starts with `ghp_`)
4. Add to Render environment variables

---

## ✅ Verify Deployment

After deployment completes:

1. **Check Health Endpoint**:
   ```bash
   curl https://your-app.onrender.com/health
   ```
   
   Should return:
   ```json
   {
     "success": true,
     "message": "GitHub Actions Test Runner API is healthy",
     "timestamp": "...",
     "environment": "production"
   }
   ```

2. **Check Logs** in Render dashboard
3. **Test from Streamlit App**

---

## 🆓 Render Free Tier

**What you get:**
- ✅ 750 hours/month (enough for 1 service)
- ✅ 512 MB RAM
- ✅ Free SSL certificate
- ⚠️ **Spins down after 15 minutes of inactivity**
- ⚠️ **Cold start takes 30-60 seconds**

**Limitations:**
- First request after inactivity will be slow
- Good for demos and occasional use
- Consider paid plan ($7/month) for production

---

## 🐛 Troubleshooting

### Service Won't Start

**Check logs in Render dashboard:**
```bash
npm ERR! missing script: start
```
**Fix:** Verify `package.json` has `"start": "node src/server.js"`

### Environment Variables Not Working

- Click "Environment" tab in Render
- Verify all variables are set
- Redeploy after adding variables

### Port Binding Issues

Render automatically sets `PORT` environment variable. Update your server:

```javascript
// In src/server.js
const PORT = process.env.PORT || 5000;
```

### CORS Errors

Add your Streamlit domain to CORS:

```javascript
app.use(cors({
  origin: [
    'http://localhost:8501',
    'https://your-app.streamlit.app'
  ]
}));
```

---

## 📊 Monitoring

**In Render Dashboard:**
- View real-time logs
- Check CPU/Memory usage
- Monitor request metrics
- Set up alerts

---

## 🔄 Updating Your Backend

**Automatic Deployments:**
Render auto-deploys when you push to `main`:

```bash
cd github-actions-backend
# Make changes
git add .
git commit -m "Update backend"
git push origin main
# Render automatically deploys
```

**Manual Deploy:**
- Go to Render dashboard
- Click "Manual Deploy" → "Deploy latest commit"

---

## 💰 Cost Comparison

| Service | Free Tier | Cold Starts | Best For |
|---------|-----------|-------------|----------|
| **Render** | 750 hrs/month | Yes (15 min) | Demos |
| **Railway** | $5/month credit | No | Light production |
| **Heroku** | No free tier | N/A | N/A |
| **Fly.io** | 3 small VMs | Minimal | Production |

**Recommendation:** Start with Render free tier, upgrade if needed.

---

## 🎯 Complete Setup Checklist

- [ ] Sign up for Render
- [ ] Connect GitHub repository
- [ ] Create Web Service with correct settings
- [ ] Add environment variables (GITHUB_TOKEN, GITHUB_USERNAME)
- [ ] Wait for deployment (3-5 minutes)
- [ ] Test health endpoint
- [ ] Copy your Render URL
- [ ] Add to Streamlit secrets as GITHUB_BACKEND_URL
- [ ] Test GitHub Actions execution from Streamlit
- [ ] Monitor logs for any issues

---

## 🔗 Useful Links

- [Render Documentation](https://render.com/docs)
- [Deploy Node.js Apps](https://render.com/docs/deploy-node-express-app)
- [Environment Variables](https://render.com/docs/environment-variables)
- [Render Status Page](https://status.render.com/)

---

## 💡 Pro Tips

1. **Keep Cold Starts Warm**: Use a service like [UptimeRobot](https://uptimerobot.com) to ping your endpoint every 5 minutes

2. **Use Render Blueprint**: Commit `render.yaml` for infrastructure as code

3. **Environment Groups**: Create reusable environment variable groups

4. **Custom Domain**: Add your own domain in Render settings (free SSL included)

5. **Health Checks**: Render automatically monitors your `/health` endpoint

---

## 🚨 Security Notes

- ✅ Never commit tokens to GitHub
- ✅ Use Render's environment variables
- ✅ Enable "Auto-Deploy" only from `main` branch
- ✅ Use secrets for sensitive data
- ✅ Regularly rotate GitHub tokens

---

**Ready to deploy?** Follow "Quick Deployment Steps" above! 🚀
