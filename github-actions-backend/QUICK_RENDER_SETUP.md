# 🚀 Quick Deploy to Render - 5 Minutes

## Step 1: Go to Render
Visit: https://dashboard.render.com/register

Sign up with GitHub (easiest option)

## Step 2: Create New Web Service

1. Click **"New +"** button (top right)
2. Select **"Web Service"**
3. Click **"Connect account"** to link your GitHub
4. Find and select: **`SarthakRay26/Automation_QA_testing`**

## Step 3: Configure Service

Fill in these fields:

| Field | Value |
|-------|-------|
| **Name** | `github-actions-backend` |
| **Region** | Choose closest to you (e.g., Oregon USA) |
| **Branch** | `main` |
| **Root Directory** | `github-actions-backend` |
| **Runtime** | `Node` (auto-detected) |
| **Build Command** | `npm install` |
| **Start Command** | `npm start` |
| **Instance Type** | `Free` |

## Step 4: Add Environment Variables

Click **"Advanced"** and add these:

```
GITHUB_TOKEN = ghp_your_personal_access_token_here
GITHUB_USERNAME = SarthakRay26
NODE_ENV = production
```

**Important:** Replace `ghp_your_personal_access_token_here` with your actual GitHub token!

### Need a token? Create one here:
https://github.com/settings/tokens/new

Required scopes:
- ✅ `repo` (all)
- ✅ `workflow`
- ✅ `delete_repo`

## Step 5: Deploy!

1. Click **"Create Web Service"**
2. Wait 3-5 minutes for deployment
3. You'll see logs in real-time
4. When done, you'll get a URL like:
   ```
   https://github-actions-backend-xyz.onrender.com
   ```

## Step 6: Test Your Backend

Open in browser or use curl:
```bash
curl https://your-app.onrender.com/health
```

Should return:
```json
{
  "success": true,
  "message": "GitHub Actions Test Runner API is healthy"
}
```

## Step 7: Connect to Streamlit

1. Go to your Streamlit Cloud app settings
2. Click **"Secrets"**
3. Add:
```toml
GITHUB_BACKEND_URL = "https://your-app.onrender.com"
GITHUB_TOKEN = "ghp_your_token"
GITHUB_USERNAME = "SarthakRay26"
```

4. Save and restart your Streamlit app

## ✅ Done!

Your full stack is now deployed:
- 🎨 **Frontend**: Streamlit Cloud
- ⚙️ **Backend**: Render
- 🤖 **Execution**: GitHub Actions

## 🔔 Important Notes

### Free Tier Behavior
- ⚠️ **Service sleeps after 15 minutes of inactivity**
- ⚠️ **First request after sleep takes 30-60 seconds (cold start)**
- ✅ **Subsequent requests are fast**

### Keep it Warm (Optional)
Use https://uptimerobot.com to ping your health endpoint every 5 minutes

### Upgrade if Needed
- **Free**: $0/month, sleeps after inactivity
- **Starter**: $7/month, always on, better performance

## 🐛 Troubleshooting

**"Build failed"?**
- Check Root Directory is `github-actions-backend`
- Verify Build Command is `npm install`

**"Service won't start"?**
- Check environment variables are set
- Look at logs in Render dashboard
- Verify GITHUB_TOKEN is valid

**"CORS error"?**
- Add your Streamlit URL to CORS_ORIGIN env var

## 📊 Monitor Your Service

In Render dashboard you can:
- View real-time logs
- Check metrics (CPU, memory)
- See request history
- Set up alerts

---

**Total Cost**: $0 (Free tier)
**Setup Time**: 5 minutes
**Maintenance**: Zero - auto-deploys on git push

Happy deploying! 🎉
