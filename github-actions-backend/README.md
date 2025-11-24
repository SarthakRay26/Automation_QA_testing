# GitHub Actions Selenium Test Runner

A production-ready Node.js/Express backend that executes Selenium test scripts using GitHub Actions workflows.

## 🚀 Features

- ✅ Create GitHub repositories programmatically
- ✅ Push Selenium test scripts and GitHub Actions workflows
- ✅ Trigger workflow executions via GitHub API
- ✅ Monitor test run status (queued, in_progress, completed, failed)
- ✅ Fetch execution logs and job details
- ✅ Clean repository management with delete functionality
- ✅ Production-ready with security, logging, and error handling

## 📁 Project Structure

```
github-actions-backend/
├── src/
│   ├── config/
│   │   └── workflow-template.yml    # GitHub Actions workflow template
│   ├── controllers/
│   │   └── testRunController.js     # Request handlers
│   ├── services/
│   │   └── githubService.js         # GitHub API integration
│   ├── routes/
│   │   └── testRuns.js              # API routes
│   └── server.js                    # Express server
├── package.json
├── .env.example
└── README.md
```

## 🔧 Setup Instructions

### 1. Install Dependencies

```bash
cd github-actions-backend
npm install
```

### 2. Configure Environment Variables

```bash
cp .env.example .env
```

Edit `.env` and add your credentials:

```env
PORT=5000
NODE_ENV=development
CORS_ORIGIN=http://localhost:3000
GITHUB_TOKEN=ghp_your_token_here
GITHUB_USERNAME=your_github_username
```

### 3. Get GitHub Personal Access Token

1. Go to: https://github.com/settings/tokens
2. Click **"Generate new token (classic)"**
3. Name: `Selenium Test Runner`
4. Select scopes:
   - ✅ `repo` (full control of repositories)
   - ✅ `workflow` (update workflows)
   - ✅ `delete_repo` (optional, for cleanup)
5. Click **"Generate token"**
6. Copy and paste into `.env` file

### 4. Start the Server

```bash
# Development mode (with auto-reload)
npm run dev

# Production mode
npm start
```

Server will start on `http://localhost:5000`

## 📡 API Endpoints

### 1. Create Test Run

**POST** `/api/create-test-run`

Creates a new GitHub repository, commits test script + workflow, and triggers execution.

**Request Body:**
```json
{
  "testScript": "from selenium import webdriver\n...",
  "testName": "my-test",
  "repoName": "selenium-test-123"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "runId": "test-run-1234567890",
    "workflowRunId": 7654321,
    "repository": "username/selenium-test-123",
    "repoUrl": "https://github.com/username/selenium-test-123",
    "workflowUrl": "https://github.com/username/selenium-test-123/actions/runs/7654321",
    "status": "queued"
  }
}
```

### 2. Get Test Run Status

**GET** `/api/status/:runId`

Returns current status of the workflow run.

**Response:**
```json
{
  "success": true,
  "data": {
    "runId": "test-run-1234567890",
    "workflowRunId": 7654321,
    "status": "completed",
    "conclusion": "success",
    "workflowUrl": "https://github.com/...",
    "createdAt": "2025-11-24T10:30:00Z",
    "updatedAt": "2025-11-24T10:35:00Z"
  }
}
```

**Status Values:**
- `queued` - Workflow is waiting to start
- `in_progress` - Test is running
- `completed` - Test finished

**Conclusion Values** (when status = completed):
- `success` - Test passed
- `failure` - Test failed
- `cancelled` - Test was cancelled

### 3. Get Test Run Logs

**GET** `/api/logs/:runId`

Fetches detailed logs and job information.

**Response:**
```json
{
  "success": true,
  "data": {
    "runId": "test-run-1234567890",
    "workflowRunId": 7654321,
    "jobs": [
      {
        "id": 12345,
        "name": "selenium-test",
        "status": "completed",
        "conclusion": "success",
        "steps": [
          {
            "name": "Checkout repository",
            "status": "completed",
            "conclusion": "success"
          },
          {
            "name": "Run Selenium test",
            "status": "completed",
            "conclusion": "success"
          }
        ]
      }
    ],
    "logDownloadUrl": "https://api.github.com/...",
    "workflowUrl": "https://github.com/..."
  }
}
```

### 4. List All Test Runs

**GET** `/api/runs`

Returns all active test runs.

**Response:**
```json
{
  "success": true,
  "data": {
    "runs": [
      {
        "runId": "test-run-1234567890",
        "workflowRunId": 7654321,
        "repository": "username/selenium-test-123",
        "status": "completed",
        "conclusion": "success",
        "createdAt": "2025-11-24T10:30:00Z"
      }
    ],
    "count": 1
  }
}
```

### 5. Delete Test Run

**DELETE** `/api/runs/:runId`

Deletes the test run and its GitHub repository.

**Response:**
```json
{
  "success": true,
  "message": "Test run and repository deleted successfully"
}
```

## 🔗 Integration Example

### Frontend (React/JavaScript)

```javascript
// Create and run a test
async function runSeleniumTest(testScript) {
  try {
    // 1. Create test run
    const response = await fetch('http://localhost:5000/api/create-test-run', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ testScript })
    });
    
    const result = await response.json();
    const { runId } = result.data;
    
    console.log('Test started:', runId);
    
    // 2. Poll for status
    const checkStatus = setInterval(async () => {
      const statusRes = await fetch(`http://localhost:5000/api/status/${runId}`);
      const statusData = await statusRes.json();
      
      console.log('Status:', statusData.data.status);
      
      if (statusData.data.status === 'completed') {
        clearInterval(checkStatus);
        
        // 3. Get logs
        const logsRes = await fetch(`http://localhost:5000/api/logs/${runId}`);
        const logsData = await logsRes.json();
        
        console.log('Test finished:', statusData.data.conclusion);
        console.log('Logs:', logsData.data);
      }
    }, 5000); // Check every 5 seconds
    
  } catch (error) {
    console.error('Error running test:', error);
  }
}
```

### Integration with Existing Python Backend

```python
import requests

def run_selenium_test_on_github(test_script: str):
    """Run Selenium test using GitHub Actions backend"""
    
    # Create test run
    response = requests.post(
        'http://localhost:5000/api/create-test-run',
        json={'testScript': test_script}
    )
    
    data = response.json()
    run_id = data['data']['runId']
    
    print(f"Test started: {run_id}")
    return run_id

# Usage with your existing FastAPI endpoint
@app.post("/run_selenium_on_github")
async def run_on_github(request: SeleniumScriptRequest):
    # Generate script using your RAG pipeline
    script = rag_pipeline.generate_selenium_script(request.test_case, html_elements)
    
    # Run on GitHub Actions
    run_id = run_selenium_test_on_github(script)
    
    return {
        "status": "success",
        "run_id": run_id,
        "message": "Test execution started on GitHub Actions"
    }
```

## 🔐 Security Best Practices

1. **Never commit `.env` file** - It's already in `.gitignore`
2. **Use environment variables** - Don't hardcode credentials
3. **Rotate GitHub tokens** - Change tokens periodically
4. **Limit token scope** - Only grant necessary permissions
5. **Use HTTPS in production** - Deploy with SSL/TLS

## 🚀 Deployment

### Deploy to Heroku

```bash
heroku create selenium-test-runner
heroku config:set GITHUB_TOKEN=your_token
heroku config:set GITHUB_USERNAME=your_username
git push heroku main
```

### Deploy to Railway

1. Connect your GitHub repository
2. Add environment variables in Railway dashboard
3. Deploy automatically on push

### Deploy to AWS/GCP/Azure

Use Docker or deploy directly:

```bash
npm install --production
NODE_ENV=production npm start
```

## 🐛 Troubleshooting

### Issue: "GITHUB_TOKEN environment variable is required"
**Solution:** Create `.env` file with your GitHub token

### Issue: "Repository already exists"
**Solution:** Change `repoName` or delete the existing repository

### Issue: Workflow not triggering
**Solution:** 
- Ensure GitHub token has `workflow` scope
- Wait 2-3 seconds after file commit before triggering
- Check repository has Actions enabled

### Issue: Can't fetch logs
**Solution:** Logs are only available after workflow completes

## 📝 License

MIT

## 🤝 Contributing

Contributions welcome! Please open an issue or PR.

---

**Built with ❤️ for automated testing**
