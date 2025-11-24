"""
Streamlit frontend for the Autonomous QA Agent.
Provides a user-friendly interface for document upload, test case generation, and Selenium script creation.
"""

import streamlit as st
import requests
import json
from typing import List, Dict, Any
from pathlib import Path

# Configure page
st.set_page_config(
    page_title="Autonomous QA Agent",
    page_icon="🤖",
    layout="wide"
)

# API Base URL
API_BASE_URL = "http://localhost:8000"


def check_api_health():
    """Check if the API is running."""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False


def upload_documents(files):
    """Upload documents to the backend."""
    files_data = [("files", (file.name, file, file.type)) for file in files]
    response = requests.post(f"{API_BASE_URL}/upload_documents", files=files_data)
    return response.json()


def upload_html(file):
    """Upload HTML file to the backend."""
    files_data = {"file": (file.name, file, file.type)}
    response = requests.post(f"{API_BASE_URL}/upload_html", files=files_data)
    return response.json()


def build_knowledge_base():
    """Build the knowledge base."""
    response = requests.post(f"{API_BASE_URL}/build_knowledge_base")
    return response.json()


def generate_test_cases(query: str, n_results: int = 5):
    """Generate test cases."""
    response = requests.post(
        f"{API_BASE_URL}/generate_test_cases",
        json={"query": query, "n_results": n_results}
    )
    return response.json()


def generate_selenium_script(test_case: Dict[str, Any]):
    """Generate Selenium script for a test case."""
    response = requests.post(
        f"{API_BASE_URL}/generate_selenium_script",
        json={"test_case": test_case}
    )
    return response.json()


def get_test_cases():
    """Get all generated test cases."""
    response = requests.get(f"{API_BASE_URL}/test_cases")
    return response.json()


def reset_system():
    """Reset the system."""
    response = requests.delete(f"{API_BASE_URL}/reset")
    return response.json()


# Main App
def main():
    st.title("🤖 Autonomous QA Agent")
    st.markdown("### RAG-based Test Case & Selenium Script Generator")
    
    # Check API health
    if not check_api_health():
        st.error("⚠️ Backend API is not running! Please start the FastAPI server.")
        st.code("cd qa_agent && python -m backend.main", language="bash")
        return
    
    st.success("✅ Backend API is running")
    
    # Sidebar
    with st.sidebar:
        st.header("📊 System Status")
        
        try:
            health = requests.get(f"{API_BASE_URL}/health").json()
            st.metric("Documents Loaded", health.get("documents_loaded", 0))
            st.metric("Test Cases Generated", health.get("test_cases_generated", 0))
            st.write(f"**HTML Loaded:** {'✅' if health.get('html_loaded') else '❌'}")
            
            st.divider()
            
            if st.button("🔄 Reset System", type="secondary"):
                with st.spinner("Resetting..."):
                    result = reset_system()
                    st.success(result.get("message", "System reset"))
                    st.rerun()
        except:
            st.warning("Could not fetch system status")
    
    # Main content tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "📁 Upload Documents",
        "🏗️ Build Knowledge Base",
        "📝 Generate Test Cases",
        "🤖 Generate Selenium Scripts"
    ])
    
    # Tab 1: Upload Documents
    with tab1:
        st.header("📁 Upload Documents")
        st.markdown("Upload your documentation files (MD, TXT, JSON, PDF)")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Upload Documentation")
            doc_files = st.file_uploader(
                "Choose documentation files",
                type=["md", "txt", "json", "pdf"],
                accept_multiple_files=True,
                key="doc_upload"
            )
            
            if st.button("📤 Upload Documents", type="primary"):
                if doc_files:
                    with st.spinner("Uploading and parsing documents..."):
                        result = upload_documents(doc_files)
                        
                        if result.get("status") == "success":
                            st.success(result.get("message"))
                            if result.get("details"):
                                st.json(result["details"])
                        else:
                            st.warning(result.get("message"))
                            if result.get("details", {}).get("errors"):
                                st.error("Errors:")
                                for error in result["details"]["errors"]:
                                    st.write(f"- {error}")
                else:
                    st.warning("Please select files to upload")
        
        with col2:
            st.subheader("Upload HTML (Optional)")
            st.markdown("Upload checkout.html or any HTML file for Selenium script generation")
            
            html_file = st.file_uploader(
                "Choose HTML file",
                type=["html"],
                key="html_upload"
            )
            
            if st.button("📤 Upload HTML", type="primary"):
                if html_file:
                    with st.spinner("Uploading and parsing HTML..."):
                        result = upload_html(html_file)
                        
                        if result.get("status") == "success":
                            st.success(result.get("message"))
                            if result.get("details"):
                                st.json(result["details"])
                        else:
                            st.error(result.get("message"))
                else:
                    st.warning("Please select an HTML file")
    
    # Tab 2: Build Knowledge Base
    with tab2:
        st.header("🏗️ Build Knowledge Base")
        st.markdown("Process uploaded documents and build the vector database for RAG")
        
        st.info("📚 This step chunks documents, generates embeddings, and stores them in ChromaDB")
        
        if st.button("🔨 Build Knowledge Base", type="primary", key="build_kb"):
            with st.spinner("Building knowledge base... This may take a few minutes..."):
                try:
                    result = build_knowledge_base()
                    
                    if result.get("status") == "success":
                        st.success(result.get("message"))
                        
                        if result.get("details"):
                            col1, col2 = st.columns(2)
                            with col1:
                                st.metric("Documents Processed", result["details"].get("documents_processed", 0))
                            with col2:
                                st.metric("Chunks Created", result["details"].get("chunks_created", 0))
                        
                        st.balloons()
                    else:
                        st.error(result.get("message"))
                        
                except Exception as e:
                    st.error(f"Error: {str(e)}")
    
    # Tab 3: Generate Test Cases
    with tab3:
        st.header("📝 Generate Test Cases")
        st.markdown("Generate test cases based on your documentation")
        
        query = st.text_area(
            "Enter your requirement/query",
            placeholder="Example: Generate test cases for discount code validation on checkout page",
            height=100
        )
        
        col1, col2 = st.columns([3, 1])
        with col1:
            n_results = st.slider("Number of context documents to retrieve", 1, 10, 5)
        
        if st.button("🚀 Generate Test Cases", type="primary", key="gen_tc"):
            if query:
                with st.spinner("Generating test cases..."):
                    try:
                        result = generate_test_cases(query, n_results)
                        
                        if result.get("status") == "success":
                            st.success(f"Generated {len(result.get('test_cases', []))} test cases")
                            
                            st.subheader("Generated Test Cases")
                            
                            for i, tc in enumerate(result.get("test_cases", []), 1):
                                with st.expander(f"Test Case {i}: {tc.get('test_id', 'N/A')} - {tc.get('feature', 'N/A')}"):
                                    st.write(f"**Test ID:** {tc.get('test_id', 'N/A')}")
                                    st.write(f"**Feature:** {tc.get('feature', 'N/A')}")
                                    st.write(f"**Scenario:** {tc.get('scenario', 'N/A')}")
                                    st.write(f"**Expected Result:** {tc.get('expected_result', 'N/A')}")
                                    st.write(f"**Grounded In:** {', '.join(tc.get('grounded_in', []))}")
                                    
                                    st.divider()
                                    
                                    # JSON view
                                    with st.container():
                                        st.json(tc)
                        else:
                            st.error(result.get("message", "Failed to generate test cases"))
                            
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
            else:
                st.warning("Please enter a query")
    
    # Tab 4: Generate Selenium Scripts
    with tab4:
        st.header("🤖 Generate Selenium Scripts")
        st.markdown("Generate Selenium test scripts from test cases")
        
        # Fetch existing test cases
        try:
            test_cases_data = get_test_cases()
            test_cases = test_cases_data.get("test_cases", [])
            
            if test_cases:
                st.subheader("Select a Test Case")
                
                # Create dropdown options
                test_case_options = {
                    f"{tc.get('test_id', 'N/A')} - {tc.get('feature', 'N/A')}": tc
                    for tc in test_cases
                }
                
                selected_tc_name = st.selectbox(
                    "Choose test case",
                    options=list(test_case_options.keys())
                )
                
                if selected_tc_name:
                    selected_tc = test_case_options[selected_tc_name]
                    
                    # Display test case details
                    with st.expander("📋 Test Case Details", expanded=True):
                        st.write(f"**Test ID:** {selected_tc.get('test_id', 'N/A')}")
                        st.write(f"**Feature:** {selected_tc.get('feature', 'N/A')}")
                        st.write(f"**Scenario:** {selected_tc.get('scenario', 'N/A')}")
                        st.write(f"**Expected Result:** {selected_tc.get('expected_result', 'N/A')}")
                    
                    if st.button("🔧 Generate Selenium Script", type="primary", key="gen_selenium"):
                        with st.spinner("Generating Selenium script..."):
                            try:
                                result = generate_selenium_script(selected_tc)
                                
                                if result.get("status") == "success":
                                    st.success("✅ Selenium script generated successfully!")
                                    
                                    script = result.get("script", "")
                                    
                                    # Store in session state
                                    st.session_state['generated_script'] = script
                                    st.session_state['test_id'] = selected_tc.get('test_id', 'case')
                                    st.session_state['html_used'] = result.get('html_elements_used', False)
                                else:
                                    st.error(result.get("message", "Failed to generate script"))
                                    
                            except Exception as e:
                                st.error(f"Error: {str(e)}")
                    
                    # Always display the script if it exists in session state
                    if st.session_state.get('generated_script'):
                        script = st.session_state['generated_script']
                        test_id = st.session_state.get('test_id', 'case')
                        html_used = st.session_state.get('html_used', False)
                        
                        st.subheader("Generated Selenium Script")
                        st.code(script, language="python")
                        
                        # Action buttons
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.download_button(
                                label="⬇️ Download Script",
                                data=script,
                                file_name=f"test_{test_id.lower().replace('-', '_')}.py",
                                mime="text/x-python"
                            )
                        
                        with col2:
                            if st.button("▶️ Run Locally", type="secondary", key="run_local_btn"):
                                st.session_state['action'] = 'run_local'
                                st.rerun()
                        
                        with col3:
                            if st.button("🚀 Run on GitHub", type="primary", key="run_github_btn"):
                                st.session_state['action'] = 'run_github'
                                st.rerun()
                        
                        # Show info about HTML elements
                        st.info(f"HTML elements {'were' if html_used else 'were not'} used in generation")
                    
                    # Handle button actions outside the generation block
                    action = st.session_state.get('action')
                    if action and st.session_state.get('generated_script'):
                        script = st.session_state['generated_script']
                        test_id = st.session_state.get('test_id', 'case')
                        
                        if action == 'run_local':
                            st.session_state['action'] = None  # Clear action
                            
                            st.divider()
                            st.subheader("🖥️ Local Execution")
                            
                            # Save script to temp file and execute
                            import tempfile
                            import subprocess
                            import os
                            import time
                            
                            status_placeholder = st.empty()
                            progress_bar = st.progress(0)
                            
                            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                                f.write(script)
                                temp_script_path = f.name
                            
                            try:
                                # Show progress
                                status_placeholder.info("🚀 Starting test execution...")
                                progress_bar.progress(10)
                                time.sleep(0.5)
                                
                                status_placeholder.info("🌐 Opening browser (Chrome)...")
                                progress_bar.progress(30)
                                
                                status_placeholder.info("🔄 Executing test steps...")
                                progress_bar.progress(50)
                                
                                process = subprocess.run(
                                    ["python3", temp_script_path],
                                    capture_output=True,
                                    text=True,
                                    timeout=60,
                                    cwd=os.path.expanduser("~/Autonomous_QA_Automation/qa_agent")
                                )
                                
                                progress_bar.progress(90)
                                time.sleep(0.3)
                                status_placeholder.empty()
                                progress_bar.progress(100)
                                time.sleep(0.3)
                                progress_bar.empty()
                                
                                if process.returncode == 0:
                                    st.success("✅ Test execution completed successfully!")
                                    if process.stdout:
                                        with st.expander("📋 Test Output", expanded=True):
                                            st.code(process.stdout, language="text")
                                else:
                                    st.error(f"❌ Test execution failed (exit code: {process.returncode})")
                                    if process.stderr:
                                        with st.expander("🔴 Error Output", expanded=True):
                                            st.code(process.stderr, language="text")
                                    if process.stdout:
                                        with st.expander("📋 Standard Output", expanded=False):
                                            st.code(process.stdout, language="text")
                            
                            except subprocess.TimeoutExpired:
                                status_placeholder.empty()
                                progress_bar.empty()
                                st.error("⏱️ Test execution timed out (60s limit)")
                            except FileNotFoundError:
                                status_placeholder.empty()
                                progress_bar.empty()
                                st.error("❌ Python3 not found.")
                            except Exception as e:
                                status_placeholder.empty()
                                progress_bar.empty()
                                st.error(f"❌ Error: {str(e)}")
                            finally:
                                try:
                                    os.unlink(temp_script_path)
                                except:
                                    pass
                        
                        elif action == 'run_github':
                            st.session_state['action'] = None  # Clear action
                            
                            st.divider()
                            st.subheader("🚀 GitHub Actions Execution")
                            
                            import time
                            status_placeholder = st.empty()
                            progress_bar = st.progress(0)
                            
                            try:
                                status_placeholder.info("📦 Creating GitHub repository...")
                                progress_bar.progress(20)
                                
                                response = requests.post(
                                    f"{API_BASE_URL}/run_selenium_on_github",
                                    json={"test_id": test_id, "script": script},
                                    timeout=30
                                )
                                
                                if response.status_code == 200:
                                    result = response.json()
                                    run_id = result.get("run_id")
                                    repo_name = result.get("repository")
                                    workflow_url = result.get("workflow_url")
                                    
                                    status_placeholder.success(f"✅ Repository: {repo_name}")
                                    progress_bar.progress(50)
                                    
                                    st.markdown(f"🔗 [View Workflow]({workflow_url})")
                                    
                                    # Poll for completion
                                    status_placeholder.info("⏳ Waiting for workflow...")
                                    max_polls = 24
                                    
                                    for i in range(max_polls):
                                        time.sleep(5)
                                        try:
                                            status_resp = requests.get(f"{API_BASE_URL}/github_run_status/{run_id}", timeout=10)
                                            if status_resp.status_code == 200:
                                                data = status_resp.json()
                                                if data.get("status") == "completed":
                                                    progress_bar.progress(100)
                                                    status_placeholder.empty()
                                                    progress_bar.empty()
                                                    
                                                    if data.get("conclusion") == "success":
                                                        st.success("✅ Workflow completed successfully!")
                                                    else:
                                                        st.warning(f"⚠️ Workflow: {data.get('conclusion')}")
                                                    
                                                    # Get logs and job details
                                                    logs_resp = requests.get(f"{API_BASE_URL}/github_run_logs/{run_id}", timeout=30)
                                                    if logs_resp.status_code == 200:
                                                        logs_data = logs_resp.json()
                                                        
                                                        # Show workflow URL prominently
                                                        workflow_url = logs_data.get("workflowUrl", workflow_url)
                                                        st.info(f"🔗 [View Full Workflow on GitHub]({workflow_url})")
                                                        
                                                        # Display job information
                                                        st.subheader("📊 Test Execution Summary")
                                                        jobs = logs_data.get("jobs", [])
                                                        
                                                        for job in jobs:
                                                            job_status = job.get("conclusion", "unknown")
                                                            job_icon = "✅" if job_status == "success" else "❌" if job_status == "failure" else "⏸️"
                                                            
                                                            with st.expander(f"{job_icon} {job.get('name', 'Job')} - {job_status}", expanded=True):
                                                                st.write(f"**Status:** {job.get('status')}")
                                                                st.write(f"**Conclusion:** {job.get('conclusion')}")
                                                                st.write(f"**Started:** {job.get('startedAt', 'N/A')}")
                                                                st.write(f"**Completed:** {job.get('completedAt', 'N/A')}")
                                                                
                                                                # Show steps
                                                                st.markdown("**Steps:**")
                                                                steps = job.get("steps", [])
                                                                for step in steps:
                                                                    step_conclusion = step.get("conclusion", "pending")
                                                                    step_icon = "✅" if step_conclusion == "success" else "❌" if step_conclusion == "failure" else "⏳"
                                                                    st.markdown(f"{step_icon} {step.get('name')} - {step_conclusion}")
                                                        
                                                        # Show log download link if available
                                                        log_download = logs_data.get("logDownloadUrl")
                                                        if log_download:
                                                            st.markdown(f"📥 [Download Complete Logs]({log_download})")
                                                        
                                                        # Fetch and display artifacts
                                                        st.subheader("📎 Test Artifacts")
                                                        try:
                                                            artifacts_resp = requests.get(f"{API_BASE_URL}/github_run_artifacts/{run_id}", timeout=10)
                                                            if artifacts_resp.status_code == 200:
                                                                artifacts_data = artifacts_resp.json()
                                                                artifacts = artifacts_data.get("artifacts", [])
                                                                
                                                                if artifacts:
                                                                    for artifact in artifacts:
                                                                        artifact_name = artifact.get("name", "Unknown")
                                                                        artifact_size = artifact.get("size", 0)
                                                                        size_kb = artifact_size / 1024
                                                                        
                                                                        st.markdown(f"**{artifact_name}** ({size_kb:.1f} KB)")
                                                                        st.caption("ℹ️ Artifacts contain test screenshots and logs. Download requires GitHub authentication.")
                                                                        st.markdown(f"🔗 [View on GitHub]({workflow_url}#artifacts)")
                                                                else:
                                                                    st.info("No artifacts available yet. Artifacts are uploaded after workflow completion.")
                                                            else:
                                                                st.warning("Could not fetch artifacts information.")
                                                        except Exception as e:
                                                            st.warning(f"Artifacts: {str(e)}")
                                                    break
                                                else:
                                                    progress_bar.progress(50 + (i * 40 // max_polls))
                                        except:
                                            pass
                                    else:
                                        status_placeholder.empty()
                                        progress_bar.empty()
                                        st.warning("⏱️ Workflow still running. Check the link above.")
                                else:
                                    status_placeholder.empty()
                                    progress_bar.empty()
                                    st.error(f"❌ Failed: {response.json().get('detail', 'Unknown error')}")
                            
                            except requests.exceptions.ConnectionError:
                                status_placeholder.empty()
                                progress_bar.empty()
                                st.error("❌ Backend not running. Start: `cd github-actions-backend && node src/server.js`")
                            except Exception as e:
                                status_placeholder.empty()
                                progress_bar.empty()
                                st.error(f"❌ Error: {str(e)}")
            else:
                st.info("📝 No test cases available. Generate test cases first in the 'Generate Test Cases' tab.")
                
        except Exception as e:
            st.error(f"Error fetching test cases: {str(e)}")
    
    # Footer
    st.divider()
    st.markdown("""
    <div style='text-align: center; color: gray;'>
        <p>Autonomous QA Agent v1.0 | RAG-based Test Automation</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
