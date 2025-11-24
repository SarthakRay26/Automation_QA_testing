"""
HTML file parser for the QA Agent.
Extracts text content and structure from .html files using BeautifulSoup.
"""

from bs4 import BeautifulSoup
from pathlib import Path
from typing import Dict, Any
import sys

sys.path.append(str(Path(__file__).parent.parent.parent))
from utils.logger import get_logger

logger = get_logger(__name__)


def parse_html(file_path: str) -> Dict[str, Any]:
    """
    Parse an HTML file and extract its content and structure.
    
    Args:
        file_path: Path to the HTML file
    
    Returns:
        Dictionary containing parsed content, HTML structure, and metadata
    """
    try:
        logger.info(f"Parsing HTML file: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Extract text content
        text_content = soup.get_text(separator='\n', strip=True)
        
        # Extract important elements for Selenium
        elements_info = {
            'ids': [elem.get('id') for elem in soup.find_all(id=True)],
            'classes': list(set([cls for elem in soup.find_all(class_=True) 
                                for cls in elem.get('class', [])])),
            'buttons': [btn.get('id') for btn in soup.find_all('button') if btn.get('id')],
            'inputs': [{'id': inp.get('id'), 'name': inp.get('name'), 
                       'type': inp.get('type', 'text')} 
                      for inp in soup.find_all('input') if inp.get('type') != 'checkbox'],
            'checkboxes': [inp.get('id') for inp in soup.find_all('input', {'type': 'checkbox'}) 
                          if inp.get('id')],
            'links': [{'text': a.text.strip(), 'href': a.get('href')} 
                     for a in soup.find_all('a')],
            'file_name': Path(file_path).name
        }
        
        result = {
            'content': text_content,
            'html_raw': html_content,
            'elements': elements_info,
            'file_name': Path(file_path).name,
            'file_type': 'html',
            'file_path': file_path
        }
        
        logger.info(f"Successfully parsed HTML file: {file_path}")
        return result
        
    except Exception as e:
        logger.error(f"Error parsing HTML file {file_path}: {str(e)}")
        raise
