"""
RAG (Retrieval-Augmented Generation) pipeline module.
Handles document chunking, retrieval, and LLM-based generation.
"""

from langchain.text_splitter import RecursiveCharacterTextSplitter
# Lazy import heavy libraries only when needed
# from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
# import torch
from typing import List, Dict, Any, Optional
from pathlib import Path
import sys
import json

sys.path.append(str(Path(__file__).parent.parent))
from utils.logger import get_logger
from backend.embeddings import EmbeddingModel
from backend.database.vector_db import VectorDatabase

logger = get_logger(__name__)


class RAGPipeline:
    """
    Complete RAG pipeline for document processing and generation.
    """
    
    def __init__(
        self,
        llm_model_name: str = "gpt2",
        embedding_model_name: str = "all-MiniLM-L6-v2",
        chunk_size: int = 500,
        chunk_overlap: int = 50
    ):
        """
        Initialize the RAG pipeline.
        
        Args:
            llm_model_name: HuggingFace model name for text generation
            embedding_model_name: SentenceTransformer model name
            chunk_size: Size of text chunks
            chunk_overlap: Overlap between chunks
        """
        logger.info("Initializing RAG Pipeline")
        
        # Store model names for lazy loading
        self.llm_model_name = llm_model_name
        self.embedding_model_name = embedding_model_name
        
        # Initialize components
        self.embedding_model = None  # Will be loaded on first use
        self.vector_db = VectorDatabase()
        self.vector_db.create_collection()
        
        # Initialize text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
        
        # LLM components - lazy loaded
        self.tokenizer = None
        self.model = None
        self.generator = None
        
        logger.info("RAG Pipeline initialized (models will load on demand)")
    
    def chunk_documents(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Split documents into chunks.
        
        Args:
            documents: List of document dictionaries with 'content' and metadata
        
        Returns:
            List of chunk dictionaries with metadata
        """
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
        
        logger.info(f"Created {len(all_chunks)} chunks from {len(documents)} documents")
        return all_chunks
    
    def build_knowledge_base(self, documents: List[Dict[str, Any]]):
        """
        Build the vector database from documents.
        
        Args:
            documents: List of document dictionaries
        """
        logger.info("Building knowledge base")
        
        # Load embedding model if not already loaded
        if self.embedding_model is None:
            logger.info(f"Loading embedding model: {self.embedding_model_name}")
            self.embedding_model = EmbeddingModel(self.embedding_model_name)
        
        # Chunk documents
        chunks = self.chunk_documents(documents)
        
        # Generate embeddings
        texts = [chunk['content'] for chunk in chunks]
        embeddings = self.embedding_model.encode(texts, show_progress_bar=True)
        
        # Prepare metadata
        metadatas = [{
            'source_file': chunk['source_file'],
            'file_type': chunk['file_type'],
            'chunk_index': chunk['chunk_index']
        } for chunk in chunks]
        
        # Generate IDs
        ids = [chunk['chunk_id'] for chunk in chunks]
        
        # Add to vector database
        self.vector_db.add_documents(
            documents=texts,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids
        )
        
        logger.info(f"Knowledge base built with {len(chunks)} chunks")
    
    def retrieve_context(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieve relevant context from the knowledge base.
        
        Args:
            query: Query string
            n_results: Number of results to retrieve
        
        Returns:
            List of relevant documents with metadata
        """
        logger.info(f"Retrieving context for query: {query[:50]}...")
        
        # Generate query embedding
        query_embedding = self.embedding_model.encode([query])
        
        # Query vector database
        results = self.vector_db.query(
            query_embeddings=query_embedding,
            n_results=n_results
        )
        
        # Format results
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
        Generate test cases based on query and retrieved context.
        
        Args:
            query: User query/requirement
            context_docs: Retrieved context documents
        
        Returns:
            List of test case dictionaries
        """
        logger.info("Generating test cases")
        
        # Load LLM if not already loaded
        if self.generator is None:
            logger.info(f"Loading LLM model: {self.llm_model_name}")
            try:
                # Import heavy libraries only when needed
                from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
                import torch
                
                self.tokenizer = AutoTokenizer.from_pretrained(self.llm_model_name)
                self.model = AutoModelForCausalLM.from_pretrained(
                    self.llm_model_name,
                    torch_dtype=torch.float32,
                    low_cpu_mem_usage=True
                )
                
                # Set pad_token if not set
                if self.tokenizer.pad_token is None:
                    self.tokenizer.pad_token = self.tokenizer.eos_token
                
                self.generator = pipeline(
                    "text-generation",
                    model=self.model,
                    tokenizer=self.tokenizer,
                    max_new_tokens=512,
                    temperature=0.7,
                    top_p=0.9,
                    do_sample=True
                )
                
                logger.info(f"Successfully loaded LLM: {self.llm_model_name}")
            except Exception as e:
                logger.error(f"Error loading LLM: {str(e)}")
                # Return default test cases if model loading fails
                return self._generate_default_test_cases(query, context_docs)
        
        # Build context string
        context_str = "\n\n".join([
            f"Source: {doc['metadata'].get('source_file', 'unknown')}\n{doc['content']}"
            for doc in context_docs
        ])
        
        # Build prompt
        prompt = f"""Based on the following documentation, generate detailed test cases for: {query}

Documentation:
{context_str}

Generate test cases in JSON format with the following structure:
{{
  "test_id": "TC-XXX",
  "feature": "Feature name",
  "scenario": "Test scenario description",
  "expected_result": "Expected outcome",
  "grounded_in": ["source_file.ext"]
}}

Generate 3-5 test cases:
"""
        
        try:
            # Generate with LLM
            response = self.generator(
                prompt,
                max_new_tokens=512,
                num_return_sequences=1,
                pad_token_id=self.tokenizer.eos_token_id
            )
            
            generated_text = response[0]['generated_text']
            
            # Extract generated portion (after prompt)
            generated_portion = generated_text[len(prompt):].strip()
            
            # Try to parse test cases from generated text
            test_cases = self._parse_test_cases(generated_portion, context_docs)
            
            logger.info(f"Generated {len(test_cases)} test cases")
            return test_cases
            
        except Exception as e:
            logger.error(f"Error generating test cases: {str(e)}")
            # Return default test cases if generation fails
            return self._generate_default_test_cases(query, context_docs)
    
    def _parse_test_cases(self, text: str, context_docs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Parse test cases from generated text.
        """
        test_cases = []
        
        # Try to extract JSON objects
        try:
            # Simple parsing - look for JSON-like structures
            lines = text.split('\n')
            for i, line in enumerate(lines):
                if '"test_id"' in line.lower() or '"feature"' in line.lower():
                    # Try to extract a test case structure
                    test_id = f"TC-{len(test_cases) + 1:03d}"
                    feature = "Generated Feature"
                    scenario = line.strip()
                    
                    test_cases.append({
                        "test_id": test_id,
                        "feature": feature,
                        "scenario": scenario,
                        "expected_result": "Should work as described",
                        "grounded_in": [doc['metadata'].get('source_file', 'unknown') 
                                       for doc in context_docs[:2]]
                    })
        except Exception as e:
            logger.warning(f"Error parsing test cases: {str(e)}")
        
        return test_cases if test_cases else self._generate_default_test_cases("", context_docs)
    
    def _generate_default_test_cases(self, query: str, context_docs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Generate default test cases when LLM generation fails.
        """
        source_files = list(set([doc['metadata'].get('source_file', 'unknown') 
                                for doc in context_docs]))
        
        return [
            {
                "test_id": "TC-001",
                "feature": f"Feature from {query[:30]}...",
                "scenario": "Verify basic functionality",
                "expected_result": "System should perform as expected",
                "grounded_in": source_files[:2] if source_files else ["documentation"]
            },
            {
                "test_id": "TC-002",
                "feature": f"Feature from {query[:30]}...",
                "scenario": "Verify error handling",
                "expected_result": "System should handle errors gracefully",
                "grounded_in": source_files[:2] if source_files else ["documentation"]
            }
        ]
    
    def generate_selenium_script(
        self,
        test_case: Dict[str, Any],
        html_elements: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate Selenium script for a test case.
        
        Args:
            test_case: Test case dictionary
            html_elements: HTML elements information from parsed HTML
        
        Returns:
            Python Selenium script as string
        """
        logger.info(f"Generating Selenium script for {test_case.get('test_id')}")
        
        # For now, always use template-based generation
        # LLM generation can be enabled later if needed
        return self._generate_default_selenium_script(test_case, html_elements)
    
    def _generate_default_selenium_script(
        self,
        test_case: Dict[str, Any],
        html_elements: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate a default Selenium script template.
        """
        script = f"""from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def test_{test_case.get('test_id', 'case').lower().replace('-', '_')}():
    \"\"\"
    Test Case: {test_case.get('test_id')}
    Feature: {test_case.get('feature')}
    Scenario: {test_case.get('scenario')}
    Expected Result: {test_case.get('expected_result')}
    \"\"\"
    
    # Initialize WebDriver
    driver = webdriver.Chrome()
    wait = WebDriverWait(driver, 10)
    
    try:
        # Navigate to the application
        driver.get("http://localhost:8000")  # Replace with actual URL
        
        # Test steps based on scenario
        # TODO: Implement specific test steps
"""
        
        # Add element-specific interactions if HTML elements are provided
        if html_elements:
            if html_elements.get('inputs'):
                script += """        
        # Fill input fields
"""
                for inp in html_elements.get('inputs', [])[:3]:
                    if inp.get('id'):
                        script += f"        input_field = wait.until(EC.presence_of_element_located((By.ID, '{inp['id']}')))\n"
                        script += f"        input_field.send_keys('test_value')\n"
            
            if html_elements.get('buttons'):
                script += """        
        # Click button
"""
                for btn in html_elements.get('buttons', [])[:1]:
                    if btn:
                        script += f"        button = wait.until(EC.element_to_be_clickable((By.XPATH, \"//button[contains(text(), '{btn}')]\")))\n"
                        script += f"        button.click()\n"
        
        script += """        
        # Wait for result
        time.sleep(2)
        
        # Verify expected result
        # TODO: Add assertions
        
        print(f"Test {test_case.get('test_id')} passed!")
        
    except Exception as e:
        print(f"Test {test_case.get('test_id')} failed: {{str(e)}}")
        raise
    
    finally:
        driver.quit()

if __name__ == "__main__":
    test_{test_case.get('test_id', 'case').lower().replace('-', '_')}()
"""
        
        return script
