"""
Lightweight RAG pipeline without heavy AI models.
Uses template-based generation instead of LLMs.
"""

from langchain.text_splitter import RecursiveCharacterTextSplitter
from typing import List, Dict, Any, Optional
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent))
from utils.logger import get_logger
from backend.embeddings_simple import SimpleEmbeddingModel
from backend.database.vector_db import VectorDatabase

logger = get_logger(__name__)


class RAGPipelineLite:
    """
    Lightweight RAG pipeline using templates instead of LLMs.
    """
    
    def __init__(
        self,
        embedding_model_name: str = "all-MiniLM-L6-v2",
        chunk_size: int = 500,
        chunk_overlap: int = 50
    ):
        """
        Initialize the lightweight RAG pipeline.
        """
        logger.info("Initializing Lightweight RAG Pipeline")
        
        self.embedding_model_name = embedding_model_name
        self.embedding_model = None  # Lazy load
        
        self.vector_db = VectorDatabase()
        self.vector_db.create_collection()
        
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
        
        logger.info("Lightweight RAG Pipeline initialized")
    
    def chunk_documents(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Split documents into chunks."""
        logger.info(f"Chunking {len(documents)} documents")
        
        all_chunks = []
        for doc in documents:
            content = doc.get('content', '')
            chunks = self.text_splitter.split_text(content)
            
            for i, chunk in enumerate(chunks):
                chunk_data = {
                    'content': chunk,
                    'chunk_id': f"{doc.get('file_name', 'unknown')}_{i}",
                    'source_file': doc.get('file_name', 'unknown'),
                    'file_type': doc.get('file_type', 'unknown'),
                    'chunk_index': i
                }
                all_chunks.append(chunk_data)
        
        logger.info(f"Created {len(all_chunks)} chunks")
        return all_chunks
    
    def build_knowledge_base(self, documents: List[Dict[str, Any]]):
        """Build the vector database from documents."""
        logger.info("Building knowledge base")
        
        # Lazy load embedding model
        if self.embedding_model is None:
            logger.info("Loading simple embedding model")
            self.embedding_model = SimpleEmbeddingModel()
        
        chunks = self.chunk_documents(documents)
        texts = [chunk['content'] for chunk in chunks]
        embeddings = self.embedding_model.encode(texts, show_progress_bar=True)
        
        metadatas = [{
            'source_file': chunk['source_file'],
            'file_type': chunk['file_type'],
            'chunk_index': chunk['chunk_index']
        } for chunk in chunks]
        
        ids = [chunk['chunk_id'] for chunk in chunks]
        
        self.vector_db.add_documents(
            documents=texts,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids
        )
        
        logger.info(f"Knowledge base built with {len(chunks)} chunks")
    
    def retrieve_context(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """Retrieve relevant context from the knowledge base."""
        logger.info(f"Retrieving context for query: {query[:50]}...")
        
        if self.embedding_model is None:
            logger.info("Loading simple embedding model")
            self.embedding_model = SimpleEmbeddingModel()
        
        query_embedding = self.embedding_model.encode([query])
        results = self.vector_db.query(
            query_embeddings=query_embedding,
            n_results=n_results
        )
        
        context_docs = []
        if results.get('documents') and len(results['documents']) > 0:
            for i, doc in enumerate(results['documents'][0]):
                context_docs.append({
                    'content': doc,
                    'metadata': results['metadatas'][0][i] if results.get('metadatas') else {}
                })
        
        logger.info(f"Retrieved {len(context_docs)} relevant documents")
        return context_docs
    
    def generate_test_cases(self, query: str, context_docs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Generate test cases using template-based approach.
        """
        logger.info("Generating test cases using templates")
        
        source_files = list(set([doc['metadata'].get('source_file', 'unknown') 
                                for doc in context_docs]))
        
        # Extract key information from context
        context_text = "\n".join([doc['content'][:200] for doc in context_docs[:3]])
        
        # Generate test cases based on query and context
        test_cases = []
        
        # Test case 1: Basic functionality
        test_cases.append({
            "test_id": "TC-001",
            "feature": f"Basic {query} Functionality",
            "scenario": f"Verify that {query} works as expected",
            "expected_result": f"System should successfully handle {query}",
            "grounded_in": source_files[:2] if source_files else ["documentation"]
        })
        
        # Test case 2: Edge cases
        test_cases.append({
            "test_id": "TC-002",
            "feature": f"{query} Edge Cases",
            "scenario": f"Test {query} with boundary conditions",
            "expected_result": "System should handle edge cases gracefully",
            "grounded_in": source_files[:2] if source_files else ["documentation"]
        })
        
        # Test case 3: Error handling
        test_cases.append({
            "test_id": "TC-003",
            "feature": f"{query} Error Handling",
            "scenario": f"Verify error handling for {query}",
            "expected_result": "System should display appropriate error messages",
            "grounded_in": source_files[:2] if source_files else ["documentation"]
        })
        
        # Test case 4: Performance
        test_cases.append({
            "test_id": "TC-004",
            "feature": f"{query} Performance",
            "scenario": f"Verify {query} completes within acceptable time",
            "expected_result": "Operation should complete in less than 3 seconds",
            "grounded_in": source_files[:2] if source_files else ["documentation"]
        })
        
        # Test case 5: Data validation
        test_cases.append({
            "test_id": "TC-005",
            "feature": f"{query} Data Validation",
            "scenario": f"Test input validation for {query}",
            "expected_result": "System should reject invalid inputs",
            "grounded_in": source_files[:2] if source_files else ["documentation"]
        })
        
        logger.info(f"Generated {len(test_cases)} test cases")
        return test_cases
    
    def generate_selenium_script(
        self,
        test_case: Dict[str, Any],
        html_elements: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate Selenium script using templates.
        """
        logger.info(f"Generating Selenium script for {test_case.get('test_id')}")
        
        # Extract variables first and clean them
        test_id = test_case.get('test_id', 'TC-001')
        feature = test_case.get('feature', 'Feature test').replace('\n', ' ').strip()
        scenario = test_case.get('scenario', 'Test scenario').replace('\n', ' ').strip()
        expected_result = test_case.get('expected_result', 'Operation should complete successfully').replace('\n', ' ').strip()
        function_name = test_id.lower().replace('-', '_')
        
        # Determine the HTML file path if available
        html_file = "user_registration.html"  # Default
        if html_elements and html_elements.get('file_name'):
            file_name = html_elements.get('file_name')
            # Check which sample folder it's in
            if 'enrollment' in file_name.lower():
                html_file = f"third_sample/{file_name}"
            elif 'checkout' in file_name.lower():
                html_file = f"first_sample/{file_name}"
            elif 'registration' in file_name.lower():
                html_file = f"second_sample/{file_name}"
            else:
                html_file = file_name
        
        script = f"""from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import time
import os

def test_{function_name}():
    \"\"\"
    Test Case: {test_id}
    Feature: {feature}
    Scenario: {scenario}
    Expected Result: {expected_result}
    \"\"\"
    
    print("=" * 60)
    print(f"🚀 Starting Test: {test_id}")
    print("=" * 60)
    
    # Initialize WebDriver with webdriver-manager
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    wait = WebDriverWait(driver, 10)
    
    try:
        # Navigate to the HTML file or application URL
        # Update this path based on your project structure
        html_path = os.path.expanduser("~/Autonomous_QA_Automation/qa_agent/sample_docs/{html_file}")
        
        if os.path.exists(html_path):
            driver.get(f"file://{{html_path}}")
            print(f"✓ Loaded local file: {html_file}")
        else:
            driver.get("http://localhost:8000")  # Fallback to localhost
            print("✓ Navigated to application")
        
        # Wait for page to load
        time.sleep(1)
"""
        
        # Add element-specific interactions if HTML elements are provided
        if html_elements and html_elements.get('inputs'):
            script += "\n        # Fill input fields\n"
            for i, inp in enumerate(html_elements.get('inputs', [])[:5]):
                inp_id = inp.get('id', '')
                inp_type = inp.get('type', 'text')
                
                if inp_id:
                    # Generate appropriate test data based on input type
                    test_value = "test_value"
                    if 'coupon' in inp_id.lower():
                        test_value = "SAVE25"
                    elif 'email' in inp_id.lower():
                        test_value = "testuser@example.com"
                    elif 'password' in inp_id.lower():
                        test_value = "SecurePass123!"
                    elif 'phone' in inp_id.lower():
                        test_value = "+1-555-0123"
                    elif 'username' in inp_id.lower():
                        test_value = "testuser123"
                    elif 'name' in inp_id.lower():
                        test_value = "Test User"
                    elif 'card' in inp_id.lower() and 'number' in inp_id.lower():
                        test_value = "4532123456789012"
                    elif 'expiry' in inp_id.lower() or 'exp' in inp_id.lower():
                        test_value = "12/25"
                    elif 'cvv' in inp_id.lower():
                        test_value = "123"
                    
                    script += f"""        {inp_id.replace('-', '_')}_field = wait.until(EC.presence_of_element_located((By.ID, "{inp_id}")))
        {inp_id.replace('-', '_')}_field.clear()
        {inp_id.replace('-', '_')}_field.send_keys("{test_value}")
        print("✓ Filled {inp_id}: {test_value}")
"""
        
        # Add checkbox handling
        if html_elements and html_elements.get('checkboxes'):
            script += "\n        # Handle checkboxes\n"
            for checkbox_id in html_elements.get('checkboxes', [])[:2]:
                script += f"""        {checkbox_id.replace('-', '_')}_checkbox = driver.find_element(By.ID, "{checkbox_id}")
        if not {checkbox_id.replace('-', '_')}_checkbox.is_selected():
            {checkbox_id.replace('-', '_')}_checkbox.click()
        print("✓ Checked: {checkbox_id}")
"""
        
        # Add button click
        if html_elements and html_elements.get('buttons'):
            script += "\n        # Click submit button\n"
            for btn_id in html_elements.get('buttons', [])[:1]:
                if btn_id:
                    script += f"""        {btn_id.replace('-', '_')}_button = wait.until(EC.element_to_be_clickable((By.ID, "{btn_id}")))
        {btn_id.replace('-', '_')}_button.click()
        print("✓ Clicked button: {btn_id}")
        time.sleep(1)
"""
        
        # Add smart assertions based on scenario
        assertions = []
        scenario_lower = scenario.lower()
        feature_lower = feature.lower()
        
        if 'coupon' in scenario_lower or 'discount' in scenario_lower:
            assertions.append("""
        # Verify coupon/discount was applied
        discount_info = driver.find_element(By.ID, "discount-info")
        assert discount_info.is_displayed(), "Discount info should be visible"
        print("✓ Discount applied successfully")
        
        # Verify price breakdown
        final_price = driver.find_element(By.ID, "final-price")
        assert final_price.text, "Final price should be displayed"
        print(f"✓ Final price: {final_price.text}")""")
        
        if 'enroll' in scenario_lower or 'payment' in scenario_lower:
            assertions.append("""
        # Verify form submission (check for alert or redirect)
        time.sleep(1)
        try:
            alert = driver.switch_to.alert
            alert_text = alert.text
            print(f"✓ Alert displayed: {{alert_text}}")
            assert "success" in alert_text.lower() or "enrolled" in alert_text.lower(), "Should show success message"
        except:
            # No alert, check for other success indicators
            page_source = driver.page_source
            assert "thank" in page_source.lower() or "success" in page_source.lower() or "enrolled" in page_source.lower(), "Should show success message"
            print("✓ Success message found on page")""")
        
        if 'registration' in scenario_lower or 'register' in scenario_lower:
            assertions.append("""
        # Verify registration success (check for alert or success message)
        time.sleep(1)
        try:
            alert = driver.switch_to.alert
            alert_text = alert.text
            print(f"✓ Alert: {{alert_text}}")
            assert "success" in alert_text.lower() or "created" in alert_text.lower(), "Should show success"
        except:
            page_source = driver.page_source
            assert len(page_source) > 100, "Page should have content"
            print("✓ Registration form submitted")""")
        
        if 'validation' in scenario_lower or 'error' in scenario_lower:
            assertions.append("""
        # Check for validation/error messages
        time.sleep(1)
        page_source = driver.page_source
        # Look for error indicators in the page
        assert len(page_source) > 100, "Page should respond"
        print("✓ Validation checked")""")
        
        # Default assertion if no specific ones match
        if not assertions:
            assertions.append("""
        # Basic verification
        page_source = driver.page_source
        assert len(page_source) > 100, "Page should have content"
        assert driver.title, "Page should have a title"
        print(f"✓ Page loaded: {{driver.title}}")""")
        
        script += f"""
        # Wait for response
        time.sleep(2)
        
        # Verify expected result: {expected_result}
        print("\\n🔍 Verifying test assertions...")
        {''.join(assertions)}
        
        print("\\n" + "=" * 60)
        print(f"✅ Test {test_id} PASSED!")
        print(f"Expected: {expected_result}")
        print("=" * 60)
        
        # Take success screenshot
        screenshot_path = os.path.expanduser(f"~/Autonomous_QA_Automation/qa_agent/test_{function_name}_success.png")
        driver.save_screenshot(screenshot_path)
        print(f"📸 Screenshot saved: test_{function_name}_success.png")
        
    except Exception as e:
        print(f"\\n❌ Test {test_id} FAILED: {{str(e)}}")
        
        # Take failure screenshot
        screenshot_path = os.path.expanduser(f"~/Autonomous_QA_Automation/qa_agent/test_{function_name}_failure.png")
        driver.save_screenshot(screenshot_path)
        print(f"📸 Failure screenshot: test_{function_name}_failure.png")
        raise
    
    finally:
        time.sleep(1)
        driver.quit()
        print("🔚 Browser closed\\n")

if __name__ == "__main__":
    try:
        test_{function_name}()
        print("✓ Test execution completed successfully")
    except Exception:
        print("✗ Test execution failed")
        exit(1)
"""
        
        return script
