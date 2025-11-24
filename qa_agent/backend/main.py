"""
FastAPI backend for the Autonomous QA Agent.
Provides REST API endpoints for document processing and test generation.
"""

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import os
import shutil
from pathlib import Path
import sys
import requests

sys.path.append(str(Path(__file__).parent.parent))
from utils.logger import get_logger
from backend.rag_lite import RAGPipelineLite
from backend.parsers.parse_md import parse_markdown
from backend.parsers.parse_txt import parse_text
from backend.parsers.parse_json import parse_json
from backend.parsers.parse_pdf import parse_pdf
from backend.parsers.parse_html import parse_html

logger = get_logger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Autonomous QA Agent API",
    description="RAG-based test case and Selenium script generator",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables
rag_pipeline: Optional[RAGPipelineLite] = None
uploaded_documents: List[Dict[str, Any]] = []
html_data: Optional[Dict[str, Any]] = None
generated_test_cases: List[Dict[str, Any]] = []

# Create uploads directory
UPLOAD_DIR = Path(__file__).parent.parent / "assets" / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


# Pydantic models
class TestCaseRequest(BaseModel):
    query: str
    n_results: int = 5


class SeleniumScriptRequest(BaseModel):
    test_case: Dict[str, Any]


class GitHubActionsRequest(BaseModel):
    test_id: str
    script: str


class StatusResponse(BaseModel):
    status: str
    message: str
    details: Optional[Dict[str, Any]] = None


@app.on_event("startup")
async def startup_event():
    """
    Initialize RAG pipeline on startup.
    """
    global rag_pipeline
    logger.info("Starting Autonomous QA Agent API")
    
    try:
        # Initialize with lazy loading - models will be loaded on first use
        logger.info("RAG Pipeline initialized successfully (models will load on demand)")
    except Exception as e:
        logger.error(f"Error initializing RAG Pipeline: {str(e)}")
        raise


@app.get("/")
async def root():
    """
    Root endpoint.
    """
    return {
        "message": "Autonomous QA Agent API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint.
    """
    return {
        "status": "healthy",
        "rag_pipeline": "initialized" if rag_pipeline else "not initialized",
        "documents_loaded": len(uploaded_documents),
        "html_loaded": html_data is not None,
        "test_cases_generated": len(generated_test_cases)
    }


@app.post("/upload_documents", response_model=StatusResponse)
async def upload_documents(files: List[UploadFile] = File(...)):
    """
    Upload and parse multiple documents (MD, TXT, JSON, PDF).
    
    Args:
        files: List of files to upload
    
    Returns:
        Status response with details
    """
    global uploaded_documents
    
    logger.info(f"Received {len(files)} files for upload")
    
    parsed_docs = []
    errors = []
    
    for file in files:
        try:
            # Save file
            file_path = UPLOAD_DIR / file.filename
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            logger.info(f"Saved file: {file.filename}")
            
            # Parse based on file extension
            ext = Path(file.filename).suffix.lower()
            
            if ext == ".md":
                parsed_doc = parse_markdown(str(file_path))
            elif ext == ".txt":
                parsed_doc = parse_text(str(file_path))
            elif ext == ".json":
                parsed_doc = parse_json(str(file_path))
            elif ext == ".pdf":
                parsed_doc = parse_pdf(str(file_path))
            else:
                errors.append(f"Unsupported file type: {file.filename}")
                continue
            
            parsed_docs.append(parsed_doc)
            logger.info(f"Successfully parsed: {file.filename}")
            
        except Exception as e:
            logger.error(f"Error processing {file.filename}: {str(e)}")
            errors.append(f"Error processing {file.filename}: {str(e)}")
    
    uploaded_documents.extend(parsed_docs)
    
    return StatusResponse(
        status="success" if parsed_docs else "partial_failure",
        message=f"Processed {len(parsed_docs)} out of {len(files)} files",
        details={
            "parsed": len(parsed_docs),
            "total": len(files),
            "errors": errors if errors else None
        }
    )


@app.post("/upload_html", response_model=StatusResponse)
async def upload_html(file: UploadFile = File(...)):
    """
    Upload and parse HTML file (e.g., checkout.html).
    
    Args:
        file: HTML file to upload
    
    Returns:
        Status response with details
    """
    global html_data
    
    logger.info(f"Received HTML file: {file.filename}")
    
    try:
        # Save file
        file_path = UPLOAD_DIR / file.filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Parse HTML
        html_data = parse_html(str(file_path))
        
        logger.info(f"Successfully parsed HTML: {file.filename}")
        
        return StatusResponse(
            status="success",
            message=f"HTML file '{file.filename}' uploaded and parsed",
            details={
                "elements_found": {
                    "ids": len(html_data.get('elements', {}).get('ids', [])),
                    "classes": len(html_data.get('elements', {}).get('classes', [])),
                    "buttons": len(html_data.get('elements', {}).get('buttons', [])),
                    "inputs": len(html_data.get('elements', {}).get('inputs', []))
                }
            }
        )
        
    except Exception as e:
        logger.error(f"Error uploading HTML: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/build_knowledge_base", response_model=StatusResponse)
async def build_knowledge_base():
    """
    Build the vector database from uploaded documents.
    
    Returns:
        Status response
    """
    global rag_pipeline, uploaded_documents
    
    # Initialize RAG pipeline on first use
    if not rag_pipeline:
        logger.info("Initializing lightweight RAG pipeline on first use...")
        try:
            rag_pipeline = RAGPipelineLite(
                embedding_model_name="all-MiniLM-L6-v2"
            )
        except Exception as e:
            logger.error(f"Error initializing RAG pipeline: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to initialize RAG pipeline: {str(e)}")
    
    if not uploaded_documents:
        raise HTTPException(status_code=400, detail="No documents uploaded")
    
    logger.info("Building knowledge base")
    
    try:
        rag_pipeline.build_knowledge_base(uploaded_documents)
        
        doc_count = rag_pipeline.vector_db.get_collection_count()
        
        logger.info(f"Knowledge base built with {doc_count} chunks")
        
        return StatusResponse(
            status="success",
            message="Knowledge base built successfully",
            details={
                "documents_processed": len(uploaded_documents),
                "chunks_created": doc_count
            }
        )
        
    except Exception as e:
        logger.error(f"Error building knowledge base: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/generate_test_cases")
async def generate_test_cases(request: TestCaseRequest):
    """
    Generate test cases based on user query.
    
    Args:
        request: Test case generation request
    
    Returns:
        List of generated test cases
    """
    global rag_pipeline, generated_test_cases
    
    if not rag_pipeline:
        raise HTTPException(status_code=500, detail="RAG pipeline not initialized")
    
    if rag_pipeline.vector_db.get_collection_count() == 0:
        raise HTTPException(status_code=400, detail="Knowledge base not built. Upload documents first.")
    
    logger.info(f"Generating test cases for query: {request.query}")
    
    try:
        # Retrieve relevant context
        context_docs = rag_pipeline.retrieve_context(request.query, request.n_results)
        
        # Generate test cases
        test_cases = rag_pipeline.generate_test_cases(request.query, context_docs)
        
        generated_test_cases = test_cases
        
        logger.info(f"Generated {len(test_cases)} test cases")
        
        return {
            "status": "success",
            "query": request.query,
            "test_cases": test_cases,
            "context_used": len(context_docs)
        }
        
    except Exception as e:
        logger.error(f"Error generating test cases: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/generate_selenium_script")
async def generate_selenium_script(request: SeleniumScriptRequest):
    """
    Generate Selenium script for a test case.
    
    Args:
        request: Selenium script generation request
    
    Returns:
        Generated Selenium script
    """
    global rag_pipeline, html_data
    
    if not rag_pipeline:
        raise HTTPException(status_code=500, detail="RAG pipeline not initialized")
    
    logger.info(f"Generating Selenium script for test case: {request.test_case.get('test_id')}")
    
    try:
        # Get HTML elements if available
        html_elements = html_data.get('elements') if html_data else None
        
        # Generate Selenium script
        script = rag_pipeline.generate_selenium_script(
            request.test_case,
            html_elements
        )
        
        logger.info("Selenium script generated successfully")
        
        return {
            "status": "success",
            "test_case_id": request.test_case.get('test_id'),
            "script": script,
            "html_elements_used": html_elements is not None
        }
        
    except Exception as e:
        logger.error(f"Error generating Selenium script: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/test_cases")
async def get_test_cases():
    """
    Get all generated test cases.
    
    Returns:
        List of test cases
    """
    return {
        "status": "success",
        "test_cases": generated_test_cases,
        "count": len(generated_test_cases)
    }


@app.delete("/reset")
async def reset_system():
    """
    Reset the system (clear documents and knowledge base).
    
    Returns:
        Status response
    """
    global uploaded_documents, html_data, generated_test_cases, rag_pipeline
    
    logger.info("Resetting system")
    
    try:
        uploaded_documents = []
        html_data = None
        generated_test_cases = []
        
        if rag_pipeline:
            rag_pipeline.vector_db.clear_collection()
            rag_pipeline.vector_db.create_collection()
        
        # Clear upload directory
        for file in UPLOAD_DIR.glob("*"):
            if file.is_file():
                file.unlink()
        
        logger.info("System reset successfully")
        
        return StatusResponse(
            status="success",
            message="System reset successfully"
        )
        
    except Exception as e:
        logger.error(f"Error resetting system: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/run_selenium_on_github")
async def run_selenium_on_github(request: GitHubActionsRequest):
    """
    Run pre-generated Selenium script on GitHub Actions.
    
    Args:
        request: GitHubActionsRequest with test_id and script
    
    Returns:
        GitHub Actions run information
    """
    try:
        # Send to Node.js GitHub Actions backend
        node_backend_url = "http://localhost:5000/api/create-test-run"
        
        response = requests.post(
            node_backend_url,
            json={
                "testScript": request.script,
                "testName": request.test_id,
                "repoName": f"selenium-test-{request.test_id}"
            },
            timeout=30
        )
        
        if response.status_code == 201:
            result = response.json()
            data = result['data']
            logger.info(f"GitHub Actions run created: {data['runId']}")
            
            # Fallback to repo URL if workflow URL is not available yet
            workflow_url = data.get('workflowUrl') or f"{data.get('repoUrl', '')}/actions"
            
            return {
                "status": "success",
                "message": "Test execution started on GitHub Actions",
                "run_id": data['runId'],
                "repository": data['repository'],
                "workflow_url": workflow_url,
                "workflow_run_id": data.get('workflowRunId'),
                "script_preview": request.script[:500] + "..." if len(request.script) > 500 else request.script
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
            result = response.json()
            # Flatten the response for easier access
            if result.get('success') and 'data' in result:
                return result['data']
            return result
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
            result = response.json()
            # Flatten the response for easier access
            if result.get('success') and 'data' in result:
                return result['data']
            return result
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


@app.get("/github_run_artifacts/{run_id}")
async def get_github_run_artifacts(run_id: str):
    """
    Get artifacts from a GitHub Actions test run.
    
    Args:
        run_id: Test run identifier
    
    Returns:
        Artifact information and download URLs
    """
    try:
        node_backend_url = f"http://localhost:5000/api/artifacts/{run_id}"
        response = requests.get(node_backend_url, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            # Flatten the response for easier access
            if result.get('success') and 'data' in result:
                return result['data']
            return result
        else:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Failed to fetch artifacts: {response.text}"
            )
            
    except requests.exceptions.ConnectionError:
        raise HTTPException(
            status_code=503,
            detail="GitHub Actions backend not available"
        )
    except Exception as e:
        logger.error(f"Error fetching GitHub run logs: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
