"""
Google Drive Integration Module
Handles authentication and file retrieval from Google Drive.
"""

import os
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
import tempfile
import shutil

try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaIoBaseDownload
    from googleapiclient.errors import HttpError
    import io
    GOOGLE_DRIVE_AVAILABLE = True
except ImportError:
    GOOGLE_DRIVE_AVAILABLE = False
    print("Warning: Google Drive libraries not installed. Install with: pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib")


# Google Drive API scopes
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']


class GoogleDriveIntegration:
    """Handle Google Drive authentication and file operations"""
    
    def __init__(self, credentials_file: Optional[str] = None, token_file: Optional[str] = None):
        """
        Initialize Google Drive integration
        
        Args:
            credentials_file: Path to Google OAuth2 credentials JSON file
            token_file: Path to store/load OAuth2 token
        """
        if not GOOGLE_DRIVE_AVAILABLE:
            raise ImportError(
                "Google Drive libraries not available. "
                "Install with: pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib"
            )
        
        self.credentials_file = credentials_file
        self.token_file = token_file or "./google_drive_token.json"
        self.service = None
        self.creds = None
        
    def authenticate(self) -> bool:
        """
        Authenticate with Google Drive API
        
        Returns:
            True if authentication successful, False otherwise
        """
        if not self.credentials_file or not os.path.exists(self.credentials_file):
            print(f"⚠ Google Drive credentials file not found: {self.credentials_file}")
            return False
        
        # Load existing token if available
        if os.path.exists(self.token_file):
            try:
                self.creds = Credentials.from_authorized_user_file(self.token_file, SCOPES)
            except Exception as e:
                print(f"⚠ Error loading existing token: {e}")
                self.creds = None
        
        # If there are no (valid) credentials available, let the user log in
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                try:
                    self.creds.refresh(Request())
                except Exception as e:
                    print(f"⚠ Error refreshing token: {e}")
                    self.creds = None
            
            if not self.creds:
                try:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_file, SCOPES
                    )
                    self.creds = flow.run_local_server(port=0)
                except Exception as e:
                    print(f"✗ Error during OAuth flow: {e}")
                    return False
            
            # Save the credentials for the next run
            try:
                with open(self.token_file, 'w') as token:
                    token.write(self.creds.to_json())
                print(f"✓ Google Drive authentication successful")
                print(f"  Token saved to: {self.token_file}")
            except Exception as e:
                print(f"⚠ Warning: Could not save token: {e}")
        
        # Build the Drive service
        try:
            self.service = build('drive', 'v3', credentials=self.creds)
            return True
        except Exception as e:
            print(f"✗ Error building Drive service: {e}")
            return False
    
    def list_files(self, folder_id: Optional[str] = None, mime_types: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        List files in Google Drive
        
        Args:
            folder_id: Optional folder ID to list files from (None = all accessible files)
            mime_types: Optional list of MIME types to filter (e.g., ['application/pdf'])
        
        Returns:
            List of file metadata dictionaries
        """
        if not self.service:
            if not self.authenticate():
                return []
        
        try:
            files = []
            page_token = None
            
            # Build query
            query_parts = []
            if folder_id:
                query_parts.append(f"'{folder_id}' in parents")
            if mime_types:
                mime_query = " or ".join([f"mimeType='{mime}'" for mime in mime_types])
                query_parts.append(f"({mime_query})")
            
            query = " and ".join(query_parts) if query_parts else None
            
            while True:
                results = self.service.files().list(
                    q=query,
                    pageSize=100,
                    fields="nextPageToken, files(id, name, mimeType, size, modifiedTime, webViewLink)",
                    pageToken=page_token
                ).execute()
                
                items = results.get('files', [])
                files.extend(items)
                
                page_token = results.get('nextPageToken')
                if not page_token:
                    break
            
            return files
        except HttpError as error:
            print(f"✗ Error listing files: {error}")
            return []
    
    def download_file(self, file_id: str, destination_path: Optional[str] = None) -> Optional[str]:
        """
        Download a file from Google Drive
        
        Args:
            file_id: Google Drive file ID
            destination_path: Optional destination path (creates temp file if not provided)
        
        Returns:
            Path to downloaded file, or None if error
        """
        if not self.service:
            if not self.authenticate():
                return None
        
        try:
            # Get file metadata
            file_metadata = self.service.files().get(fileId=file_id).execute()
            file_name = file_metadata.get('name', 'unknown_file')
            mime_type = file_metadata.get('mimeType', '')
            
            # Determine destination
            if not destination_path:
                # Create temp file with appropriate extension
                suffix = self._get_file_extension(file_name, mime_type)
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
                destination_path = temp_file.name
                temp_file.close()
            
            # Download file
            request = self.service.files().get_media(fileId=file_id)
            with open(destination_path, 'wb') as f:
                downloader = MediaIoBaseDownload(f, request)
                done = False
                while not done:
                    status, done = downloader.next_chunk()
            
            print(f"✓ Downloaded: {file_name} -> {destination_path}")
            return destination_path
            
        except HttpError as error:
            print(f"✗ Error downloading file {file_id}: {error}")
            return None
    
    def download_files_from_folder(self, folder_id: str, destination_dir: str, 
                                   mime_types: Optional[List[str]] = None) -> List[str]:
        """
        Download all files from a Google Drive folder
        
        Args:
            folder_id: Google Drive folder ID
            destination_dir: Directory to save files
            mime_types: Optional list of MIME types to filter
        
        Returns:
            List of paths to downloaded files
        """
        files = self.list_files(folder_id=folder_id, mime_types=mime_types)
        downloaded_paths = []
        
        destination_path = Path(destination_dir)
        destination_path.mkdir(parents=True, exist_ok=True)
        
        for file_info in files:
            file_id = file_info['id']
            file_name = file_info['name']
            dest_path = destination_path / file_name
            
            # Avoid overwriting - add number if exists
            counter = 1
            original_dest = dest_path
            while dest_path.exists():
                stem = original_dest.stem
                suffix = original_dest.suffix
                dest_path = destination_path / f"{stem}_{counter}{suffix}"
                counter += 1
            
            downloaded = self.download_file(file_id, str(dest_path))
            if downloaded:
                downloaded_paths.append(downloaded)
        
        return downloaded_paths
    
    def _get_file_extension(self, file_name: str, mime_type: str) -> str:
        """Get file extension from name or MIME type"""
        # Try from filename first
        if '.' in file_name:
            return Path(file_name).suffix
        
        # Map common MIME types to extensions
        mime_to_ext = {
            'application/pdf': '.pdf',
            'application/vnd.google-apps.document': '.docx',
            'application/vnd.google-apps.spreadsheet': '.xlsx',
            'application/vnd.google-apps.presentation': '.pptx',
            'text/plain': '.txt',
            'text/csv': '.csv',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document': '.docx',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': '.xlsx',
            'message/rfc822': '.eml',
        }
        
        return mime_to_ext.get(mime_type, '')
    
    def export_google_doc(self, file_id: str, mime_type: str, destination_path: str) -> Optional[str]:
        """
        Export Google Docs/Sheets/Slides to a specific format
        
        Args:
            file_id: Google Drive file ID
            mime_type: Target MIME type (e.g., 'application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
            destination_path: Destination file path
        
        Returns:
            Path to exported file, or None if error
        """
        if not self.service:
            if not self.authenticate():
                return None
        
        try:
            request = self.service.files().export_media(fileId=file_id, mimeType=mime_type)
            with open(destination_path, 'wb') as f:
                downloader = MediaIoBaseDownload(f, request)
                done = False
                while not done:
                    status, done = downloader.next_chunk()
            
            return destination_path
        except HttpError as error:
            print(f"✗ Error exporting file {file_id}: {error}")
            return None


def get_supported_mime_types() -> List[str]:
    """Get list of MIME types supported by the document processor"""
    return [
        'application/pdf',
        'text/plain',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'application/msword',
        'message/rfc822',
        'application/vnd.ms-outlook',
        'text/csv',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'application/vnd.ms-excel',
        # Google Workspace formats (will be exported)
        'application/vnd.google-apps.document',
        'application/vnd.google-apps.spreadsheet',
        'application/vnd.google-apps.presentation',
    ]
