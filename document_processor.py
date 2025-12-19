"""
Document Processing Module
Handles ingestion and processing of various document types for the litigation system.
"""

import os
import re
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path
import email
from email import policy
import json

try:
    import PyPDF2
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

try:
    from docx import Document as DocxDocument
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False


class DocumentProcessor:
    """Process various document types and extract metadata"""
    
    def __init__(self):
        self.supported_types = {
            '.pdf': self._process_pdf,
            '.txt': self._process_text,
            '.doc': self._process_docx,  # Will try to process as docx
            '.docx': self._process_docx,
            '.eml': self._process_email,
            '.msg': self._process_email,
            '.csv': self._process_csv,
            '.xlsx': self._process_excel,
            '.xls': self._process_excel,
        }
    
    def process_document(self, file_path: str) -> Dict[str, Any]:
        """Process a document and return extracted content and metadata"""
        try:
            file_path = str(file_path)
            if not os.path.exists(file_path):
                return {
                    'success': False,
                    'error': f'File not found: {file_path}'
                }
            
            file_ext = Path(file_path).suffix.lower()
            
            if file_ext not in self.supported_types:
                return {
                    'success': False,
                    'error': f'Unsupported file type: {file_ext}'
                }
            
            processor = self.supported_types[file_ext]
            result = processor(file_path)
            
            # Extract additional metadata
            result['parties'] = self._extract_parties(result.get('content', ''))
            result['dates'] = self._extract_dates(result.get('content', ''))
            result['topics'] = self._extract_topics(result.get('content', ''))
            result['doc_type'] = self._classify_document(result.get('content', ''), file_ext)
            
            result['success'] = True
            return result
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'content': '',
                'doc_type': 'unknown'
            }
    
    def _process_pdf(self, file_path: str) -> Dict[str, Any]:
        """Extract text from PDF"""
        if not PDF_AVAILABLE:
            return {
                'content': '',
                'error': 'PyPDF2 not installed. Install with: pip install PyPDF2'
            }
        
        try:
            content_parts = []
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    content_parts.append(page.extract_text())
            
            content = '\n'.join(content_parts)
            return {'content': content}
        except Exception as e:
            return {'content': '', 'error': str(e)}
    
    def _process_text(self, file_path: str) -> Dict[str, Any]:
        """Extract text from plain text file"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                content = file.read()
            return {'content': content}
        except Exception as e:
            return {'content': '', 'error': str(e)}
    
    def _process_docx(self, file_path: str) -> Dict[str, Any]:
        """Extract text from Word document"""
        if not DOCX_AVAILABLE:
            return {
                'content': '',
                'error': 'python-docx not installed. Install with: pip install python-docx'
            }
        
        try:
            doc = DocxDocument(file_path)
            content_parts = []
            for paragraph in doc.paragraphs:
                content_parts.append(paragraph.text)
            content = '\n'.join(content_parts)
            return {'content': content}
        except Exception as e:
            return {'content': '', 'error': str(e)}
    
    def _process_email(self, file_path: str) -> Dict[str, Any]:
        """Extract content from email file"""
        try:
            with open(file_path, 'rb') as file:
                msg = email.message_from_bytes(file.read(), policy=policy.default)
            
            content_parts = []
            
            # Extract headers
            content_parts.append(f"From: {msg.get('From', 'Unknown')}")
            content_parts.append(f"To: {msg.get('To', 'Unknown')}")
            content_parts.append(f"Subject: {msg.get('Subject', 'No Subject')}")
            content_parts.append(f"Date: {msg.get('Date', 'Unknown')}")
            content_parts.append("")
            
            # Extract body
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                        content_parts.append(part.get_payload(decode=True).decode('utf-8', errors='ignore'))
            else:
                content_parts.append(msg.get_payload(decode=True).decode('utf-8', errors='ignore'))
            
            content = '\n'.join(content_parts)
            return {'content': content}
        except Exception as e:
            return {'content': '', 'error': str(e)}
    
    def _process_csv(self, file_path: str) -> Dict[str, Any]:
        """Extract content from CSV file"""
        if not PANDAS_AVAILABLE:
            return {
                'content': '',
                'error': 'pandas not installed. Install with: pip install pandas'
            }
        
        try:
            df = pd.read_csv(file_path)
            content = df.to_string()
            return {'content': content}
        except Exception as e:
            return {'content': '', 'error': str(e)}
    
    def _process_excel(self, file_path: str) -> Dict[str, Any]:
        """Extract content from Excel file"""
        if not PANDAS_AVAILABLE:
            return {
                'content': '',
                'error': 'pandas not installed. Install with: pip install pandas'
            }
        
        try:
            df = pd.read_excel(file_path)
            content = df.to_string()
            return {'content': content}
        except Exception as e:
            return {'content': '', 'error': str(e)}
    
    def _extract_parties(self, content: str) -> List[str]:
        """Extract party names from content (simple pattern matching)"""
        parties = []
        
        # Common legal party patterns
        patterns = [
            r'(?:Plaintiff|Defendant|Appellant|Appellee|Petitioner|Respondent)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
            r'([A-Z][a-z]+\s+[A-Z][a-z]+)\s+v\.\s+([A-Z][a-z]+\s+[A-Z][a-z]+)',
            r'(?:Mr\.|Ms\.|Mrs\.|Dr\.)\s+([A-Z][a-z]+\s+[A-Z][a-z]+)',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content)
            if isinstance(matches[0], tuple) if matches else False:
                parties.extend([m for match in matches for m in match if m])
            else:
                parties.extend(matches)
        
        return list(set(parties))[:10]  # Limit to 10 unique parties
    
    def _extract_dates(self, content: str) -> List[str]:
        """Extract dates from content"""
        dates = []
        
        # Various date patterns
        patterns = [
            r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}',
            r'\d{4}[/-]\d{1,2}[/-]\d{1,2}',
            r'(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}',
            r'\d{1,2}\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content)
            dates.extend(matches)
        
        return list(set(dates))[:20]  # Limit to 20 unique dates
    
    def _extract_topics(self, content: str) -> List[str]:
        """Extract topics/keywords from content"""
        # Simple keyword extraction based on legal terms
        legal_keywords = [
            'contract', 'agreement', 'lawsuit', 'litigation', 'settlement',
            'breach', 'damages', 'injunction', 'motion', 'pleading',
            'discovery', 'deposition', 'testimony', 'evidence', 'exhibit',
            'bankruptcy', 'creditor', 'debtor', 'foreclosure', 'lien',
            'rico', 'racketeering', 'fraud', 'conspiracy', 'transaction'
        ]
        
        content_lower = content.lower()
        found_topics = [keyword for keyword in legal_keywords if keyword in content_lower]
        
        return found_topics[:10]  # Limit to 10 topics
    
    def _classify_document(self, content: str, file_ext: str) -> str:
        """Classify document type based on content and extension"""
        content_lower = content.lower()
        
        # Classification rules
        if 'email' in content_lower or file_ext in ['.eml', '.msg']:
            return 'email'
        elif 'motion' in content_lower or 'pleading' in content_lower:
            return 'court_filing'
        elif 'contract' in content_lower or 'agreement' in content_lower:
            return 'contract'
        elif 'invoice' in content_lower or 'payment' in content_lower:
            return 'financial_record'
        elif 'deposition' in content_lower or 'testimony' in content_lower:
            return 'deposition'
        elif file_ext == '.pdf':
            return 'pdf_document'
        elif file_ext in ['.csv', '.xlsx', '.xls']:
            return 'financial_record'
        else:
            return 'general_document'

