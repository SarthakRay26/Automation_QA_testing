"""
GitHub Actions integration endpoint for FastAPI backend
Add this to your existing main.py
"""

import requests
from typing import Optional

# Add this to your existing main.py after other endpoints

@app.post("/run_selenium_on_github")
async def run_selenium_on_github(request: SeleniumScriptRequest):
    """
    Generate Selenium script and run it on GitHub Actions.
    
    Args:
        request: SeleniumScriptRequest with test_case details
    
    Returns:
        GitHub Actions run information
    """
    global rag_pipeline, html_data
    
    if not rag_pipeline:
        raise HTTPException(status_code=500, detail="RAG pipeline not initialized")
    
    try:
        # Generate Selenium script using existing RAG pipeline
        script = rag_pipeline.generate_selenium_script(
            request.test_case,
            html_data
        )
        
        # Send to Node.js GitHub Actions backend
        node_backend_url = "http://localhost:5000/api/create-test-run"
        
        response = requests.post(
            node_backend_url,
            json={
                "testScript": script,
                "testName": request.test_case.get('test_id', 'selenium-test'),
                "repoName": f"selenium-test-{request.test_case.get('test_id', 'default')}"
            },
            timeout=30
        )
        
        if response.status_code == 201:
            result = response.json()
            logger.info(f"GitHub Actions run created: {result['data']['runId']}")
            
            return {
                "status": "success",
                "message": "Test execution started on GitHub Actions",
                "github_run": result['data'],
                "script_preview": script[:500] + "..." if len(script) > 500 else script
            }
        else:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Failed to create GitHub Actions run: {response.text}"
            )
            
    except requests.exceptions.ConnectionError:
        raise HTTPException(
            status_code=503,
            detail="GitHub Actions backend not available. Start Node.js server: cd github-actions-backend && npm start"
        )
    except Exception as e:
        logger.error(f"Error running on GitHub Actions: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/github_run_status/{run_id}")
async def get_github_run_status(run_id: str):
    """
    Get status of a GitHub Actions test run.
    
    Args:
        run_id: Test run identifier
    
    Returns:
        Run status and details
    """
    try:
        node_backend_url = f"http://localhost:5000/api/status/{run_id}"
        
        response = requests.get(node_backend_url, timeout=10)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Failed to fetch status: {response.text}"
            )
            
    except requests.exceptions.ConnectionError:
        raise HTTPException(
            status_code=503,
            detail="GitHub Actions backend not available"
        )
    except Exception as e:
        logger.error(f"Error fetching GitHub run status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/github_run_logs/{run_id}")
async def get_github_run_logs(run_id: str):
    """
    Get logs from a GitHub Actions test run.
    
    Args:
        run_id: Test run identifier
    
    Returns:
        Execution logs and job details
    """
    try:
        node_backend_url = f"http://localhost:5000/api/logs/{run_id}"
        
        response = requests.get(node_backend_url, timeout=10)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Failed to fetch logs: {response.text}"
            )
            
    except requests.exceptions.ConnectionError:
        raise HTTPException(
            status_code=503,
            detail="GitHub Actions backend not available"
        )
    except Exception as e:
        logger.error(f"Error fetching GitHub run logs: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
