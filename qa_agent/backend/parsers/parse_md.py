"""
Markdown file parser for the QA Agent.
Extracts text content from .md files.
"""

from pathlib import Path
from typing import Dict, Any
import sys

sys.path.append(str(Path(__file__).parent.parent.parent))
from utils.logger import get_logger

logger = get_logger(__name__)


def parse_markdown(file_path: str) -> Dict[str, Any]:
    """
    Parse a markdown file and extract its content.
    
    Args:
        file_path: Path to the markdown file
    
    Returns:
        Dictionary containing parsed content and metadata
    """
    try:
        logger.info(f"Parsing markdown file: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        result = {
            'content': content,
            'file_name': Path(file_path).name,
            'file_type': 'markdown',
            'file_path': file_path
        }
        
        logger.info(f"Successfully parsed markdown file: {file_path}")
        return result
        
    except Exception as e:
        logger.error(f"Error parsing markdown file {file_path}: {str(e)}")
        raise
