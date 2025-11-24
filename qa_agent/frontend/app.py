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
                                    
                                    st.subheader("Generated Selenium Script")
                                    st.code(script, language="python")
                                    
                                    # Download button
                                    col1, col2 = st.columns(2)
                                    
                                    with col1:
                                        st.download_button(
                                            label="⬇️ Download Script",
                                            data=script,
                                            file_name=f"test_{selected_tc.get('test_id', 'case').lower().replace('-', '_')}.py",
                                            mime="text/x-python"
                                        )
                                    
                                    with col2:
                                        if st.button("▶️ Run Script", type="secondary", key="run_script"):
                                            # Save script to temp file and execute
                                            import tempfile
                                            import subprocess
                                            import os
                                            
                                            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                                                f.write(script)
                                                temp_script_path = f.name
                                            
                                            try:
                                                # Run script in background and show status
                                                with st.spinner("🔄 Executing Selenium test (may open browser)..."):
                                                    process = subprocess.run(
                                                        ["python3", temp_script_path],
                                                        capture_output=True,
                                                        text=True,
                                                        timeout=60,
                                                        cwd=os.path.expanduser("~/Autonomous_QA_Automation/qa_agent")
                                                    )
                                                    
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
                                                st.error("⏱️ Test execution timed out (60s limit)")
                                                st.info("💡 Tip: Complex tests may need more time. Download and run manually for longer tests.")
                                            except FileNotFoundError:
                                                st.error("❌ Python3 not found. Please ensure Python is installed.")
                                            except Exception as e:
                                                st.error(f"❌ Error running script: {str(e)}")
                                                st.info("💡 Try downloading the script and running it manually.")
                                            finally:
                                                # Clean up temp file
                                                try:
                                                    os.unlink(temp_script_path)
                                                except:
                                                    pass
                                    
                                    st.info(f"HTML elements {'were' if result.get('html_elements_used') else 'were not'} used in generation")
                                else:
                                    st.error(result.get("message", "Failed to generate script"))
                                    
                            except Exception as e:
                                st.error(f"Error: {str(e)}")
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
