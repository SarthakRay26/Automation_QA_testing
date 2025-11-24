# Autonomous QA Agent 🤖

A complete RAG-based (Retrieval-Augmented Generation) test automation system that generates test cases and Selenium scripts from documentation.

## 📋 Overview

The Autonomous QA Agent is a full-stack application that leverages:
- **RAG Pipeline**: Retrieves relevant context from your documentation
- **Vector Database**: ChromaDB for efficient semantic search
- **LLM Generation**: HuggingFace models for test case and script generation
- **Browser Automation**: Selenium for executable test scripts

### Key Features

✅ **Document Processing**: Supports MD, TXT, JSON, PDF, and HTML files  
✅ **Smart Chunking**: Uses RecursiveCharacterTextSplitter for optimal context  
✅ **Semantic Search**: SentenceTransformers for accurate embeddings  
✅ **Test Case Generation**: AI-generated test cases grounded in your docs  
✅ **Selenium Scripts**: Automated generation of executable test scripts  
✅ **Web Interface**: User-friendly Streamlit frontend  
✅ **REST API**: FastAPI backend with complete CRUD operations  

## 🏗️ Architecture

```
qa_agent/
├── backend/
│   ├── main.py              # FastAPI server with REST endpoints
│   ├── rag.py               # RAG pipeline implementation
│   ├── embeddings.py        # SentenceTransformers wrapper
│   ├── parsers/             # Document parsers (MD, TXT, JSON, PDF, HTML)
│   │   ├── parse_md.py
│   │   ├── parse_txt.py
│   │   ├── parse_json.py
│   │   ├── parse_pdf.py
│   │   └── parse_html.py
│   └── database/
│       └── vector_db.py     # ChromaDB operations
├── frontend/
│   └── app.py               # Streamlit UI
├── utils/
│   └── logger.py            # Logging utility
├── assets/                  # Uploaded files storage
├── models/                  # Model cache directory
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## 🚀 Installation & Setup

### Prerequisites

- Python 3.8+
- pip package manager
- 4GB+ RAM (for LLM models)

### Step 1: Clone or Navigate to Project

```bash
cd /Users/sarthakray/Autonomous_QA_Automation/qa_agent
```

### Step 2: Create Virtual Environment

```bash
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
# venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

**Note**: Initial installation may take 5-10 minutes as it downloads ML models.

### Step 4: Verify Installation

```bash
python -c "import fastapi, streamlit, chromadb, sentence_transformers; print('✅ All dependencies installed')"
```

## 🎯 Usage Guide

### Starting the Application

You need to run **both** the backend and frontend:

#### Terminal 1: Start FastAPI Backend

```bash
cd qa_agent
python -m backend.main
```

The API will be available at: `http://localhost:8000`

API Documentation: `http://localhost:8000/docs`

#### Terminal 2: Start Streamlit Frontend

```bash
cd qa_agent
streamlit run frontend/app.py
```

The UI will open in your browser at: `http://localhost:8501`

### Workflow

#### 1. Upload Documents 📁

Upload your documentation files:
- **Markdown** (.md): Product specs, feature docs
- **Text** (.txt): Requirements, notes
- **JSON** (.json): API specs, config files
- **PDF** (.pdf): User manuals, design docs
- **HTML** (.html): Checkout pages, web forms

**Example documents to upload:**
- `product_requirements.md`
- `api_specification.json`
- `user_manual.pdf`
- `checkout.html` (for Selenium scripts)

#### 2. Build Knowledge Base 🏗️

Click "Build Knowledge Base" to:
- Chunk documents into manageable pieces
- Generate embeddings using SentenceTransformers
- Store in ChromaDB vector database

This process may take a few minutes depending on document size.

#### 3. Generate Test Cases 📝

Enter a query describing what you want to test:

**Example queries:**
- "Generate test cases for discount code validation"
- "Test cases for user login functionality"
- "Verify payment processing workflow"

The system will:
- Retrieve relevant context from your docs
- Generate comprehensive test cases
- Ground each test case in source documents

**Generated Test Case Format:**
```json
{
  "test_id": "TC-001",
  "feature": "Discount Code Validation",
  "scenario": "Apply valid discount code SAVE15",
  "expected_result": "Should reduce total price by 15%",
  "grounded_in": ["product_specs.md", "checkout.html"]
}
```

#### 4. Generate Selenium Scripts 🤖

Select a test case and click "Generate Selenium Script" to:
- Retrieve HTML structure (if uploaded)
- Generate executable Python + Selenium code
- Use correct element selectors (ID, name, XPath)

**Generated script includes:**
- WebDriver setup
- Element locators
- Test actions
- Assertions
- Error handling

## 📚 API Documentation

### Endpoints

#### `GET /health`
Check API health and system status

#### `POST /upload_documents`
Upload multiple documents (MD, TXT, JSON, PDF)
- **Body**: multipart/form-data with files
- **Returns**: Upload status and parsing results

#### `POST /upload_html`
Upload HTML file for Selenium generation
- **Body**: multipart/form-data with single HTML file
- **Returns**: Parsed HTML elements (IDs, classes, buttons, inputs)

#### `POST /build_knowledge_base`
Build vector database from uploaded documents
- **Returns**: Number of documents processed and chunks created

#### `POST /generate_test_cases`
Generate test cases based on query
- **Body**: `{"query": "your query", "n_results": 5}`
- **Returns**: List of generated test cases with context

#### `POST /generate_selenium_script`
Generate Selenium script for a test case
- **Body**: `{"test_case": {...}}`
- **Returns**: Python Selenium script as string

#### `GET /test_cases`
Get all generated test cases
- **Returns**: List of all test cases

#### `DELETE /reset`
Reset system (clear documents and knowledge base)
- **Returns**: Success status

### Example API Usage

```python
import requests

# Upload documents
with open('product_spec.md', 'rb') as f:
    files = {'files': ('product_spec.md', f, 'text/markdown')}
    response = requests.post('http://localhost:8000/upload_documents', files=files)
    print(response.json())

# Build knowledge base
response = requests.post('http://localhost:8000/build_knowledge_base')
print(response.json())

# Generate test cases
response = requests.post(
    'http://localhost:8000/generate_test_cases',
    json={"query": "test discount codes", "n_results": 5}
)
test_cases = response.json()['test_cases']

# Generate Selenium script
response = requests.post(
    'http://localhost:8000/generate_selenium_script',
    json={"test_case": test_cases[0]}
)
script = response.json()['script']
print(script)
```

## 🧪 Running Generated Selenium Scripts

1. Install Selenium WebDriver:
```bash
pip install selenium webdriver-manager
```

2. Save generated script to file:
```bash
# Copy script from UI or API response
cat > test_tc001.py << 'EOF'
# Paste generated script here
EOF
```

3. Install ChromeDriver (or your preferred browser):
```bash
pip install webdriver-manager
```

4. Run the test:
```bash
python test_tc001.py
```

## 📖 Supported Document Types

### Markdown (.md)
Best for: Feature specifications, README files, documentation
```markdown
# Feature: Discount Codes
Users can apply discount codes at checkout...
```

### Text (.txt)
Best for: Plain text requirements, notes
```
Requirements for login feature:
- Username validation
- Password encryption
```

### JSON (.json)
Best for: API specs, configuration files, structured data
```json
{
  "feature": "checkout",
  "discount_codes": ["SAVE10", "SAVE15"]
}
```

### PDF (.pdf)
Best for: User manuals, design documents, scanned docs

### HTML (.html)
Best for: Web pages, forms - essential for Selenium script generation
```html
<form id="checkout-form">
  <input id="discount-code" name="discount" />
  <button id="apply-discount">Apply</button>
</form>
```

## 🔧 Configuration

### Changing LLM Model

Edit `backend/rag.py`:
```python
rag_pipeline = RAGPipeline(
    llm_model_name="gpt2",  # Change to "facebook/opt-125m", "EleutherAI/gpt-neo-125M", etc.
    embedding_model_name="all-MiniLM-L6-v2"
)
```

### Adjusting Chunk Size

Edit `backend/rag.py`:
```python
self.text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,      # Increase for more context per chunk
    chunk_overlap=50,    # Increase for better continuity
    length_function=len
)
```

### Changing API Port

Edit `backend/main.py`:
```python
uvicorn.run(app, host="0.0.0.0", port=8000)  # Change port here
```

## 🐛 Troubleshooting

### "Backend API is not running"
- Ensure FastAPI server is started: `python -m backend.main`
- Check port 8000 is not in use: `lsof -i :8000`

### "Collection not initialized"
- Upload documents first
- Click "Build Knowledge Base"
- Wait for process to complete

### "Error loading LLM"
- Ensure sufficient RAM (4GB+)
- Try smaller model: `gpt2` instead of larger models
- Check internet connection for initial download

### Import Errors
```bash
# Reinstall dependencies
pip install --upgrade -r requirements.txt
```

### ChromaDB Errors
```bash
# Clear ChromaDB and restart
rm -rf chroma_db/
python -m backend.main
```

## 📊 Performance Tips

1. **Document Size**: Keep individual documents under 10MB for faster processing
2. **Chunk Size**: Smaller chunks (300-500) for precise retrieval, larger (800-1000) for more context
3. **Model Selection**: 
   - Fast: `gpt2` (default)
   - Balanced: `facebook/opt-125m`
   - Quality: `EleutherAI/gpt-neo-1.3B` (requires more RAM)

## 🤝 Contributing

### Project Structure Guidelines

- **Modular Code**: Each file has a single responsibility
- **Docstrings**: All functions include comprehensive docstrings
- **Type Hints**: Use type hints for better code clarity
- **Error Handling**: Try-except blocks with proper logging
- **Async Support**: FastAPI endpoints use async where beneficial

### Adding New Parsers

1. Create parser in `backend/parsers/parse_<format>.py`
2. Implement `parse_<format>(file_path) -> Dict[str, Any]`
3. Add to `backend/main.py` upload endpoint
4. Update README with new format

## 📄 License

This project is created for educational and testing purposes.

## 🙏 Acknowledgments

- **FastAPI**: High-performance web framework
- **Streamlit**: Rapid UI development
- **ChromaDB**: Efficient vector database
- **HuggingFace**: Pre-trained models and transformers
- **Selenium**: Browser automation

## 📞 Support

For issues or questions:
1. Check the Troubleshooting section
2. Review API docs at `http://localhost:8000/docs`
3. Check logs in `logs/` directory

---

**Built with ❤️ using RAG, LLMs, and modern Python stack**
