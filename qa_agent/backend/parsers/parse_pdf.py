"""
PDF file parser for the QA Agent.
Extracts text content from .pdf files using PyMuPDF.
"""

import fitz  # PyMuPDF
from pathlib import Path
from typing import Dict, Any
import sys

sys.path.append(str(Path(__file__).parent.parent.parent))
from utils.logger import get_logger

logger = get_logger(__name__)


def parse_pdf(file_path: str) -> Dict[str, Any]:
    """
    Parse a PDF file and extract its text content.
    
    Args:
        file_path: Path to the PDF file
    
    Returns:
        Dictionary containing parsed content and metadata
    """
    try:
        logger.info(f"Parsing PDF file: {file_path}")
        
        doc = fitz.open(file_path)
        content = ""
        
        # Extract text from each page
        for page_num in range(len(doc)):
            page = doc[page_num]
            content += f"\n--- Page {page_num + 1} ---\n"
            content += page.get_text()
        
        doc.close()
        
        result = {
            'content': content.strip(),
            'file_name': Path(file_path).name,
            'file_type': 'pdf',
            'file_path': file_path,
            'num_pages': len(doc)
        }
        
        logger.info(f"Successfully parsed PDF file: {file_path} ({len(doc)} pages)")
        return result
        
    except Exception as e:
        logger.error(f"Error parsing PDF file {file_path}: {str(e)}")
        raise
