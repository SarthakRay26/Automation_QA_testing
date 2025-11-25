# Deployment Guide - Autonomous QA Agent

## Architecture Overview

The system consists of 3 services:
1. **FastAPI Backend** (Port 8000) - RAG pipeline, test generation
2. **Node.js Backend** (Port 5000) - GitHub Actions integration
3. **Streamlit UI** (Port 8501) - User interface

## Prerequisites

- Python 3.9+
- Node.js 18+
- Git
- GitHub Personal Access Token

## Environment Setup

### 1. FastAPI Backend (.env)

Create `qa_agent/backend/.env`:
```bash
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000

# Optional: LLM API keys if using external models
# OPENAI_API_KEY=your_key_here
```

### 2. Node.js Backend (.env)

Create `github-actions-backend/.env`:
```bash
PORT=5000
NODE_ENV=production
GITHUB_TOKEN=your_github_personal_access_token
GITHUB_USERNAME=your_github_username
```

**To create GitHub token:**
1. Go to GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Click "Generate new token"
3. Select scopes: `repo` (full control), `workflow`, `delete_repo`
4. Copy the token and add to .env

## Installation

### 1. Install Python Dependencies

```bash
cd qa_agent/backend
pip3 install -r requirements.txt

cd ../frontend
pip3 install streamlit requests
```

### 2. Install Node.js Dependencies

```bash
cd github-actions-backend
npm install
```

## Running Services

### Production Deployment

#### Option 1: Using PM2 (Recommended)

Install PM2:
```bash
npm install -g pm2
```

Start all services:
```bash
# FastAPI Backend
cd qa_agent/backend
pm2 start "python3 -m uvicorn main:app --host 0.0.0.0 --port 8000" --name qa-fastapi

# Node.js Backend
cd ../../github-actions-backend
pm2 start src/server.js --name qa-nodejs

# Streamlit UI
cd ../qa_agent/frontend
pm2 start "python3 -m streamlit run app.py --server.port 8501 --server.headless true" --name qa-streamlit

# Save configuration
pm2 save
pm2 startup
```

Monitor services:
```bash
pm2 status
pm2 logs qa-fastapi
pm2 logs qa-nodejs
pm2 logs qa-streamlit
```

#### Option 2: Using systemd (Linux)

Create service files in `/etc/systemd/system/`:

**qa-fastapi.service:**
```ini
[Unit]
Description=QA Agent FastAPI Backend
After=network.target

[Service]
Type=simple
User=your_user
WorkingDirectory=/path/to/Autonomous_QA_Automation/qa_agent/backend
Environment="PATH=/usr/bin:/usr/local/bin"
ExecStart=/usr/bin/python3 -m uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

**qa-nodejs.service:**
```ini
[Unit]
Description=QA Agent Node.js Backend
After=network.target

[Service]
Type=simple
User=your_user
WorkingDirectory=/path/to/Autonomous_QA_Automation/github-actions-backend
Environment="NODE_ENV=production"
ExecStart=/usr/bin/node src/server.js
Restart=always

[Install]
WantedBy=multi-user.target
```

**qa-streamlit.service:**
```ini
[Unit]
Description=QA Agent Streamlit UI
After=network.target

[Service]
Type=simple
User=your_user
WorkingDirectory=/path/to/Autonomous_QA_Automation/qa_agent/frontend
ExecStart=/usr/bin/python3 -m streamlit run app.py --server.port 8501 --server.headless true
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable qa-fastapi qa-nodejs qa-streamlit
sudo systemctl start qa-fastapi qa-nodejs qa-streamlit
```

### Development Mode

```bash
# Terminal 1 - FastAPI
cd qa_agent/backend
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Terminal 2 - Node.js
cd github-actions-backend
node src/server.js

# Terminal 3 - Streamlit
cd qa_agent/frontend
python3 -m streamlit run app.py --server.port 8501
```

## Nginx Configuration (Optional)

If deploying on a server with domain:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # Streamlit UI
    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # FastAPI Backend
    location /api/ {
        proxy_pass http://localhost:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # Node.js Backend
    location /github/ {
        proxy_pass http://localhost:5000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Verification

1. Check services are running:
```bash
curl http://localhost:8000/health
curl http://localhost:5000/health
curl http://localhost:8501
```

2. Access UI: http://localhost:8501 or http://your-domain.com

## Troubleshooting

### Services not starting

Check logs:
```bash
# PM2
pm2 logs

# systemd
journalctl -u qa-fastapi -f
journalctl -u qa-nodejs -f
journalctl -u qa-streamlit -f
```

### Port conflicts

```bash
# Check what's using ports
lsof -i :8000
lsof -i :5000
lsof -i :8501

# Kill processes if needed
lsof -ti:8000 | xargs kill -9
```

### GitHub Actions not working

1. Verify GITHUB_TOKEN in .env
2. Check token permissions (repo, workflow, delete_repo)
3. Check Node.js logs: `pm2 logs qa-nodejs`

## Security Considerations

1. **Never commit .env files** to git
2. Use HTTPS with SSL certificate for production
3. Set up firewall rules to restrict access
4. Rotate GitHub token regularly
5. Use environment-specific tokens (dev vs prod)

## Monitoring

### Health Checks

All services provide health endpoints:
- FastAPI: `http://localhost:8000/health`
- Node.js: `http://localhost:5000/health`
- Streamlit: `http://localhost:8501`

### PM2 Monitoring

```bash
pm2 monit           # Real-time monitoring
pm2 status          # Service status
pm2 logs            # View all logs
```

## Backup & Maintenance

### Database Backups

The system stores test cases in memory. For persistence:
1. Use Redis or PostgreSQL for test case storage
2. Backup vector database (ChromaDB) regularly

### Clean up test repositories

```bash
# List all selenium-test repos
gh repo list --limit 1000 | grep selenium-test

# Delete old test repos
gh repo delete username/selenium-test-TC-XXX
```

## Scaling

For production at scale:
1. Use Docker containers
2. Deploy behind load balancer
3. Use Redis for session management
4. Use PostgreSQL for test case storage
5. Implement queue system (Celery/RabbitMQ) for test execution

## Support

For issues:
1. Check logs first
2. Verify environment variables
3. Check GitHub token permissions
4. Review network/firewall settings
