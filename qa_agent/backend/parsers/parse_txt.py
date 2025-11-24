"""
Text file parser for the QA Agent.
Extracts text content from .txt files.
"""

from pathlib import Path
from typing import Dict, Any
import sys

sys.path.append(str(Path(__file__).parent.parent.parent))
from utils.logger import get_logger

logger = get_logger(__name__)


def parse_text(file_path: str) -> Dict[str, Any]:
    """
    Parse a text file and extract its content.
    
    Args:
        file_path: Path to the text file
    
    Returns:
        Dictionary containing parsed content and metadata
    """
    try:
        logger.info(f"Parsing text file: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        result = {
            'content': content,
            'file_name': Path(file_path).name,
            'file_type': 'text',
            'file_path': file_path
        }
        
        logger.info(f"Successfully parsed text file: {file_path}")
        return result
        
    except Exception as e:
        logger.error(f"Error parsing text file {file_path}: {str(e)}")
        raise
