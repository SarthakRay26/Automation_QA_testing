"""
JSON file parser for the QA Agent.
Extracts and formats content from .json files.
"""

import json
from pathlib import Path
from typing import Dict, Any
import sys

sys.path.append(str(Path(__file__).parent.parent.parent))
from utils.logger import get_logger

logger = get_logger(__name__)


def parse_json(file_path: str) -> Dict[str, Any]:
    """
    Parse a JSON file and extract its content.
    
    Args:
        file_path: Path to the JSON file
    
    Returns:
        Dictionary containing parsed content and metadata
    """
    try:
        logger.info(f"Parsing JSON file: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
        
        # Convert JSON to readable text format
        content = json.dumps(json_data, indent=2)
        
        result = {
            'content': content,
            'json_data': json_data,
            'file_name': Path(file_path).name,
            'file_type': 'json',
            'file_path': file_path
        }
        
        logger.info(f"Successfully parsed JSON file: {file_path}")
        return result
        
    except Exception as e:
        logger.error(f"Error parsing JSON file {file_path}: {str(e)}")
        raise
