"""
Autonomous QA Agent - Streamlit Cloud Deployment Version
Combines frontend and backend functionality for Streamlit Cloud hosting.
"""

import streamlit as st
import requests
import json
import base64
import time
from typing import List, Dict, Any
from pathlib import Path
import os

# Configure page
st.set_page_config(
    page_title="Autonomous QA Agent",
    page_icon="🤖",
    layout="wide"
)

# Initialize session state
if 'github_token' not in st.session_state:
    st.session_state.github_token = None
if 'github_username' not in st.session_state:
    st.session_state.github_username = None
if 'generated_script' not in st.session_state:
    st.session_state.generated_script = None
if 'test_id' not in st.session_state:
    st.session_state.test_id = None

# GitHub Actions Backend URL (keep Node.js backend separate or deploy on another service)
# For Streamlit Cloud, you'll need to deploy the Node.js backend separately (e.g., Railway, Render, Heroku)
GITHUB_BACKEND_URL = os.getenv("GITHUB_BACKEND_URL", "http://localhost:5000")


def get_github_credentials():
    """Get GitHub credentials from Streamlit secrets or user input."""
    # Try to get from Streamlit secrets first
    try:
        token = st.secrets.get("GITHUB_TOKEN")
        username = st.secrets.get("GITHUB_USERNAME")
        if token and username:
            st.session_state.github_token = token
            st.session_state.github_username = username
            return token, username
    except:
        pass
    
    # If not in secrets, show input fields
    with st.sidebar:
        st.subheader("🔐 GitHub Configuration")
        token = st.text_input("GitHub Token", type="password", value=st.session_state.github_token or "")
        username = st.text_input("GitHub Username", value=st.session_state.github_username or "")
        
        if token and username:
            st.session_state.github_token = token
            st.session_state.github_username = username
            return token, username
    
    return None, None


def trigger_github_workflow(test_id: str, script: str):
    """Trigger GitHub Actions workflow."""
    token, username = get_github_credentials()
    
    if not token or not username:
        st.error("Please configure GitHub credentials in the sidebar")
        return None
    
    try:
        response = requests.post(
            f"{GITHUB_BACKEND_URL}/api/create-test-run",
            json={
                "test_id": test_id,
                "script": script
            },
            headers={
                "Authorization": f"Bearer {token}",
                "X-GitHub-Username": username
            },
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Failed to trigger workflow: {response.text}")
            return None
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return None


def check_workflow_status(run_id: str):
    """Check GitHub Actions workflow status."""
    try:
        response = requests.get(f"{GITHUB_BACKEND_URL}/api/status/{run_id}", timeout=10)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        st.error(f"Error checking status: {str(e)}")
        return None


def main():
    st.title("🤖 Autonomous QA Testing Agent")
    st.markdown("### Generate and Execute Selenium Test Scripts using AI")
    
    # Check GitHub backend connectivity
    try:
        health_check = requests.get(f"{GITHUB_BACKEND_URL}/health", timeout=5)
        if health_check.status_code != 200:
            st.warning(f"⚠️ GitHub Actions backend is not available at {GITHUB_BACKEND_URL}")
            st.info("GitHub execution features will be disabled. You can still generate scripts.")
    except:
        st.warning(f"⚠️ Cannot connect to GitHub Actions backend at {GITHUB_BACKEND_URL}")
        st.info("To enable GitHub execution, deploy the Node.js backend and set GITHUB_BACKEND_URL")
    
    # Sidebar
    with st.sidebar:
        st.header("📋 Instructions")
        st.markdown("""
        1. **Configure GitHub** (optional for cloud execution)
        2. **Upload documents** for context
        3. **Upload HTML** file to test
        4. **Generate test cases** from documents
        5. **Generate Selenium script** from test case
        6. **Run locally** or **Run on GitHub Actions**
        """)
        
        st.divider()
        st.markdown("### 🔗 Quick Links")
        st.markdown("- [GitHub Repo](https://github.com/SarthakRay26/Automation_QA_testing)")
        st.markdown("- [Documentation](https://github.com/SarthakRay26/Automation_QA_testing/blob/main/DEPLOYMENT.md)")
    
    # Main content tabs
    tab1, tab2, tab3 = st.tabs(["📝 Generate Scripts", "🚀 Execute Tests", "📊 View Results"])
    
    with tab1:
        st.header("Script Generation")
        
        # Document upload
        st.subheader("1. Upload Documentation (Optional)")
        uploaded_files = st.file_uploader(
            "Upload requirement documents",
            type=["txt", "md", "pdf", "json"],
            accept_multiple_files=True
        )
        
        # HTML upload
        st.subheader("2. Upload HTML to Test")
        html_file = st.file_uploader("Upload HTML file", type=["html"])
        
        # Manual test case input
        st.subheader("3. Define Test Case")
        test_case_json = st.text_area(
            "Enter test case in JSON format:",
            value="""{
    "test_id": "TC001",
    "title": "Verify form submission",
    "description": "Test form with all fields",
    "preconditions": ["Browser is open", "Page is loaded"],
    "test_steps": [
        "Enter text in coupon-code field",
        "Enter card number in card-number field",
        "Click submit button"
    ],
    "expected_results": ["Form submits successfully"]
}""",
            height=300
        )
        
        # Generate script button
        if st.button("🎯 Generate Selenium Script", type="primary"):
            try:
                test_case = json.loads(test_case_json)
                
                # Generate basic Selenium script template
                script = generate_selenium_script(test_case)
                
                st.session_state.generated_script = script
                st.session_state.test_id = test_case.get("test_id", "TC001")
                
                st.success("✅ Script generated successfully!")
                
            except json.JSONDecodeError:
                st.error("Invalid JSON format. Please check your test case.")
            except Exception as e:
                st.error(f"Error: {str(e)}")
    
    with tab2:
        st.header("Execute Tests")
        
        if st.session_state.generated_script:
            st.subheader("Generated Script:")
            st.code(st.session_state.generated_script, language="python")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.download_button(
                    label="📥 Download Script",
                    data=st.session_state.generated_script,
                    file_name=f"{st.session_state.test_id}.py",
                    mime="text/x-python"
                )
            
            with col2:
                if st.button("🚀 Run on GitHub Actions", type="primary"):
                    token, username = get_github_credentials()
                    
                    if not token or not username:
                        st.error("Please configure GitHub credentials in the sidebar")
                    else:
                        with st.spinner("Triggering GitHub Actions workflow..."):
                            result = trigger_github_workflow(
                                st.session_state.test_id,
                                st.session_state.generated_script
                            )
                            
                            if result:
                                st.success(f"✅ Workflow triggered successfully!")
                                st.json(result)
                                
                                # Store run_id for status checking
                                if 'data' in result and 'run_id' in result['data']:
                                    st.session_state.current_run_id = result['data']['run_id']
        else:
            st.info("👈 Generate a script first in the 'Generate Scripts' tab")
    
    with tab3:
        st.header("Test Results")
        
        if 'current_run_id' in st.session_state:
            run_id = st.session_state.current_run_id
            
            if st.button("🔄 Check Status"):
                with st.spinner("Checking workflow status..."):
                    status = check_workflow_status(run_id)
                    
                    if status:
                        st.json(status)
                        
                        # Display workflow URL
                        if 'data' in status and 'html_url' in status['data']:
                            st.markdown(f"[View on GitHub]({status['data']['html_url']})")
                    else:
                        st.error("Failed to fetch status")
        else:
            st.info("No active test runs. Execute a test first in the 'Execute Tests' tab")


def generate_selenium_script(test_case: Dict[str, Any]) -> str:
    """Generate a basic Selenium script from test case."""
    test_id = test_case.get("test_id", "TC001")
    title = test_case.get("title", "Test")
    description = test_case.get("description", "")
    test_steps = test_case.get("test_steps", [])
    
    script = f'''"""
Test Case: {test_id}
Title: {title}
Description: {description}
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriver, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time

def setup_driver():
    """Initialize Chrome WebDriver with options."""
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    driver = webdriver.Chrome(options=options)
    return driver

def test_{test_id.lower()}():
    """
    {title}
    """
    driver = setup_driver()
    
    try:
        # Navigate to page
        driver.get("http://localhost:8000/test.html")
        wait = WebDriverWait(driver, 10)
        
        print(f"Test {test_id}: {title}")
        print("=" * 50)
        
'''
    
    # Generate steps
    for i, step in enumerate(test_steps, 1):
        step_lower = step.lower()
        
        if "enter" in step_lower or "input" in step_lower or "type" in step_lower:
            if "coupon" in step_lower:
                script += f'''        # Step {i}: {step}
        coupon_field = wait.until(EC.presence_of_element_located((By.ID, "coupon-code")))
        coupon_field.clear()
        coupon_field.send_keys("TEST123")
        print("✓ Entered coupon code")
        
'''
            elif "card" in step_lower:
                script += f'''        # Step {i}: {step}
        card_field = wait.until(EC.presence_of_element_located((By.ID, "card-number")))
        card_field.clear()
        card_field.send_keys("4111111111111111")
        print("✓ Entered card number")
        
'''
            elif "email" in step_lower:
                script += f'''        # Step {i}: {step}
        email_field = wait.until(EC.presence_of_element_located((By.ID, "email")))
        email_field.clear()
        email_field.send_keys("test@example.com")
        print("✓ Entered email")
        
'''
        
        elif "click" in step_lower:
            if "submit" in step_lower or "button" in step_lower:
                script += f'''        # Step {i}: {step}
        submit_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']")))
        submit_button.click()
        print("✓ Clicked submit button")
        time.sleep(2)
        
'''
    
    script += '''        # Verify success
        success_msg = driver.find_element(By.ID, "message")
        assert "success" in success_msg.text.lower(), "Form submission failed"
        print("✓ Test passed successfully!")
        
        driver.save_screenshot(f"{test_id}_success.png")
        return True
        
    except Exception as e:
        print(f"✗ Test failed: {str(e)}")
        driver.save_screenshot(f"{test_id}_failure.png")
        return False
        
    finally:
        driver.quit()

if __name__ == "__main__":
    success = test_''' + test_id.lower() + '''()
    exit(0 if success else 1)
'''
    
    return script


if __name__ == "__main__":
    main()
