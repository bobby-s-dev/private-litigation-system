"""
Private AI Litigation Knowledge System
A comprehensive, secure AI assistant for organizing, analyzing, and supporting 
factual development for multiple overlapping legal cases.
"""

import gradio as gr
import os
import json
import shutil
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import pandas as pd

# Import configuration module for environment variables and secrets
try:
    from config import Config
    print("✓ Configuration module loaded")
except ImportError as e:
    print(f"⚠ Warning: Could not import config module: {e}")
    print("  Authentication and environment variables will not be available")
    Config = None

# Import our custom modules
try:
    from document_processor import DocumentProcessor
    from knowledge_base import KnowledgeBase
    from ai_analyzer import AIAnalyzer
    
    # Initialize core components
    doc_processor = DocumentProcessor()
    
    # Use knowledge base directory from config if available
    kb_dir = Config.KNOWLEDGE_BASE_DIR if Config else "./knowledge_base"
    knowledge_base = KnowledgeBase(storage_dir=kb_dir)
    ai_analyzer = AIAnalyzer()
    
    # Initialize Google Drive integration if enabled
    google_drive = None
    if Config and Config.GOOGLE_DRIVE_ENABLED:
        try:
            from google_drive_integration import GoogleDriveIntegration
            credentials_file = Config.GOOGLE_DRIVE_CREDENTIALS_FILE
            token_file = Config.GOOGLE_DRIVE_TOKEN_FILE
            if credentials_file:
                google_drive = GoogleDriveIntegration(
                    credentials_file=credentials_file,
                    token_file=token_file
                )
                print("✓ Google Drive integration initialized")
            else:
                print("⚠ Google Drive enabled but GOOGLE_DRIVE_CREDENTIALS_FILE not set")
        except ImportError as e:
            print(f"⚠ Google Drive libraries not available: {e}")
        except Exception as e:
            print(f"⚠ Error initializing Google Drive: {e}")
    
    # Create documents storage directory for permanent file storage
    # Use directory from config if available
    if Config:
        DOCUMENTS_STORAGE_DIR = Path(Config.DOCUMENTS_STORAGE_DIR)
    else:
        DOCUMENTS_STORAGE_DIR = Path("./uploaded_documents")
    DOCUMENTS_STORAGE_DIR.mkdir(exist_ok=True)
    print("✓ All modules loaded successfully")
    print(f"✓ Documents will be saved to: {DOCUMENTS_STORAGE_DIR.absolute()}")
except ImportError as e:
    print(f"✗ Import error: {e}")
    print("Make sure document_processor.py, knowledge_base.py, and ai_analyzer.py are in the same directory")
    raise
except Exception as e:
    print(f"✗ Error initializing modules: {e}")
    raise

# Global state
uploaded_documents = []
document_metadata = {}


def process_uploaded_files(files):
    """Process uploaded files and extract content"""
    if files is None:
        return "No files uploaded", []
    
    processed_files = []
    status_messages = []
    
    for file in files:
        try:
            file_path = file.name if hasattr(file, 'name') else file
            file_name = os.path.basename(file_path)
            
            # Save original file to permanent storage
            try:
                import shutil
                # Create a safe filename (remove invalid characters)
                safe_filename = "".join(c for c in file_name if c.isalnum() or c in "._- ")
                # Add timestamp to avoid conflicts
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                name_parts = safe_filename.rsplit('.', 1)
                if len(name_parts) == 2:
                    safe_filename = f"{name_parts[0]}_{timestamp}.{name_parts[1]}"
                else:
                    safe_filename = f"{safe_filename}_{timestamp}"
                
                permanent_path = DOCUMENTS_STORAGE_DIR / safe_filename
                shutil.copy2(file_path, permanent_path)
                permanent_file_path = str(permanent_path.absolute())
            except Exception as e:
                permanent_file_path = file_path  # Fallback to original path
                status_messages.append(f"⚠ {file_name} - Could not save to permanent storage: {str(e)}")
            
            # Process document (use permanent path if available)
            process_path = permanent_file_path if permanent_file_path != file_path else file_path
            result = doc_processor.process_document(process_path)
            
            if result['success']:
                # Store in knowledge base
                doc_id = knowledge_base.add_document(
                    content=result['content'],
                    metadata={
                        'file_name': file_name,
                        'file_path': permanent_file_path,
                        'original_path': file_path,
                        'doc_type': result['doc_type'],
                        'upload_date': datetime.now().isoformat(),
                        'parties': result.get('parties', []),
                        'dates': result.get('dates', []),
                        'topics': result.get('topics', [])
                    }
                )
                
                uploaded_documents.append({
                    'id': doc_id,
                    'name': file_name,
                    'type': result['doc_type'],
                    'status': 'Processed'
                })
                
                document_metadata[doc_id] = result
                status_messages.append(f"✓ {file_name} - {result['doc_type']} processed successfully")
                if permanent_file_path != file_path:
                    status_messages.append(f"  📁 Saved to: {permanent_file_path}")
            else:
                status_messages.append(f"✗ {file_name} - Error: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            status_messages.append(f"✗ {file_name} - Exception: {str(e)}")
    
    status_text = "\n".join(status_messages)
    doc_list = [[doc['name'], doc['type'], doc['status']] for doc in uploaded_documents]
    
    return status_text, doc_list


def import_from_google_drive(folder_id: Optional[str] = None, file_types: Optional[List[str]] = None):
    """Import documents from Google Drive"""
    if not google_drive:
        return "Google Drive integration is not enabled or configured. Check your .env file.", []
    
    try:
        # Authenticate if needed
        if not google_drive.service:
            auth_result = google_drive.authenticate()
            if not auth_result:
                return "Failed to authenticate with Google Drive. Please check your credentials.", []
        
        # Use folder ID from config if not provided
        if not folder_id and Config and Config.GOOGLE_DRIVE_FOLDER_ID:
            folder_id = Config.GOOGLE_DRIVE_FOLDER_ID
        
        # Get supported MIME types
        from google_drive_integration import get_supported_mime_types
        supported_mimes = file_types if file_types else get_supported_mime_types()
        
        # List files
        status_messages = []
        status_messages.append("📥 Fetching files from Google Drive...")
        
        files = google_drive.list_files(folder_id=folder_id, mime_types=supported_mimes)
        
        if not files:
            return "No supported files found in Google Drive.", []
        
        status_messages.append(f"✓ Found {len(files)} file(s) in Google Drive")
        
        # Download and process files
        processed_files = []
        for file_info in files:
            file_id = file_info['id']
            file_name = file_info['name']
            mime_type = file_info.get('mimeType', '')
            
            try:
                # Create temp directory for downloads
                temp_dir = DOCUMENTS_STORAGE_DIR / "google_drive_temp"
                temp_dir.mkdir(exist_ok=True)
                
                # Determine if it's a Google Workspace file that needs export
                is_google_doc = mime_type.startswith('application/vnd.google-apps.')
                
                if is_google_doc:
                    # Export Google Docs/Sheets/Slides
                    export_mime = 'application/pdf'  # Default export format
                    file_ext = '.pdf'
                    if 'document' in mime_type:
                        export_mime = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
                        file_ext = '.docx'
                    elif 'spreadsheet' in mime_type:
                        export_mime = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                        file_ext = '.xlsx'
                    elif 'presentation' in mime_type:
                        export_mime = 'application/pdf'
                        file_ext = '.pdf'
                    
                    # Remove existing extension if present and add correct one
                    base_name = file_name.rsplit('.', 1)[0] if '.' in file_name else file_name
                    dest_path = temp_dir / f"{base_name}{file_ext}"
                    downloaded_path = google_drive.export_google_doc(file_id, export_mime, str(dest_path))
                else:
                    # Regular file download
                    dest_path = temp_dir / file_name
                    downloaded_path = google_drive.download_file(file_id, str(dest_path))
                
                if downloaded_path:
                    # Process the downloaded file
                    result = doc_processor.process_document(downloaded_path)
                    
                    if result['success']:
                        # Move to permanent storage
                        safe_filename = "".join(c for c in file_name if c.isalnum() or c in "._- ")
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        name_parts = safe_filename.rsplit('.', 1)
                        if len(name_parts) == 2:
                            safe_filename = f"{name_parts[0]}_{timestamp}.{name_parts[1]}"
                        else:
                            safe_filename = f"{safe_filename}_{timestamp}"
                        
                        permanent_path = DOCUMENTS_STORAGE_DIR / safe_filename
                        shutil.move(downloaded_path, permanent_path)
                        
                        # Store in knowledge base
                        doc_id = knowledge_base.add_document(
                            content=result['content'],
                            metadata={
                                'file_name': file_name,
                                'file_path': str(permanent_path.absolute()),
                                'source': 'google_drive',
                                'google_drive_id': file_id,
                                'doc_type': result['doc_type'],
                                'upload_date': datetime.now().isoformat(),
                                'parties': result.get('parties', []),
                                'dates': result.get('dates', []),
                                'topics': result.get('topics', [])
                            }
                        )
                        
                        uploaded_documents.append({
                            'id': doc_id,
                            'name': file_name,
                            'type': result['doc_type'],
                            'status': 'Processed'
                        })
                        
                        document_metadata[doc_id] = result
                        processed_files.append([file_name, result['doc_type'], 'Processed'])
                        status_messages.append(f"✓ {file_name} - Processed successfully")
                    else:
                        status_messages.append(f"✗ {file_name} - Error: {result.get('error', 'Unknown error')}")
                else:
                    status_messages.append(f"✗ {file_name} - Failed to download")
                    
            except Exception as e:
                status_messages.append(f"✗ {file_name} - Exception: {str(e)}")
        
        status_text = "\n".join(status_messages)
        return status_text, processed_files
        
    except Exception as e:
        return f"Error importing from Google Drive: {str(e)}", []


def list_google_drive_files(folder_id: Optional[str] = None):
    """List files available in Google Drive"""
    if not google_drive:
        return "Google Drive integration is not enabled or configured.", []
    
    try:
        # Authenticate if needed
        if not google_drive.service:
            auth_result = google_drive.authenticate()
            if not auth_result:
                return "Failed to authenticate with Google Drive.", []
        
        # Use folder ID from config if not provided
        if not folder_id and Config and Config.GOOGLE_DRIVE_FOLDER_ID:
            folder_id = Config.GOOGLE_DRIVE_FOLDER_ID
        
        from google_drive_integration import get_supported_mime_types
        files = google_drive.list_files(folder_id=folder_id, mime_types=get_supported_mime_types())
        
        if not files:
            return "No supported files found in Google Drive.", []
        
        file_list = []
        for file_info in files:
            file_list.append([
                file_info.get('name', 'Unknown'),
                file_info.get('mimeType', 'Unknown'),
                file_info.get('size', 'N/A'),
                file_info.get('modifiedTime', 'N/A')[:10] if file_info.get('modifiedTime') else 'N/A'
            ])
        
        return f"Found {len(files)} file(s) in Google Drive:", file_list
        
    except Exception as e:
        return f"Error listing Google Drive files: {str(e)}", []


def query_knowledge_base(query: str, search_type: str = "semantic"):
    """Query the knowledge base with different search types"""
    if not query or not query.strip():
        return "Please enter a query.", ""
    
    try:
        if search_type == "semantic":
            results = knowledge_base.semantic_search(query, top_k=5)
        elif search_type == "keyword":
            results = knowledge_base.keyword_search(query, top_k=5)
        else:
            results = knowledge_base.hybrid_search(query, top_k=5)
        
        if not results:
            return "No results found.", ""
        
        # Format results
        formatted_results = []
        sources = []
        
        for i, result in enumerate(results, 1):
            doc_info = result.get('metadata', {})
            content = result.get('content', '')[:500] + "..." if len(result.get('content', '')) > 500 else result.get('content', '')
            
            formatted_results.append(
                f"**Result {i}** (Relevance: {result.get('score', 0):.3f})\n"
                f"Document: {doc_info.get('file_name', 'Unknown')}\n"
                f"Type: {doc_info.get('doc_type', 'Unknown')}\n"
                f"Content: {content}\n"
                f"{'─' * 50}\n"
            )
            sources.append(doc_info.get('file_name', 'Unknown'))
        
        response_text = "\n".join(formatted_results)
        sources_text = "\n".join([f"• {s}" for s in set(sources)])
        
        return response_text, sources_text
        
    except Exception as e:
        return f"Error querying knowledge base: {str(e)}", ""


def ask_question(message: str, history: List):
    """Chat interface for asking questions about the legal documents"""
    if not message or not message.strip():
        return ""
    
    try:
        # Use AI analyzer to generate comprehensive response
        response = ai_analyzer.answer_question(
            question=message,
            knowledge_base=knowledge_base,
            chat_history=history
        )
        
        return response
        
    except Exception as e:
        return f"Error generating response: {str(e)}"


def build_timeline(query: str, date_range: Optional[Tuple[str, str]] = None):
    """Build a chronological timeline of events"""
    if not query or not query.strip():
        return "Please enter a query to build timeline.", pd.DataFrame()
    
    try:
        # Search for relevant documents
        results = knowledge_base.semantic_search(query, top_k=20)
        
        # Extract events with dates
        events = []
        for result in results:
            metadata = result.get('metadata', {})
            dates = metadata.get('dates', [])
            content = result.get('content', '')
            
            for date_str in dates:
                events.append({
                    'Date': date_str,
                    'Event': content[:200] + "..." if len(content) > 200 else content,
                    'Document': metadata.get('file_name', 'Unknown'),
                    'Type': metadata.get('doc_type', 'Unknown'),
                    'Parties': ', '.join(metadata.get('parties', []))
                })
        
        if not events:
            return "No timeline events found for this query.", pd.DataFrame()
        
        # Create DataFrame and sort by date
        df = pd.DataFrame(events)
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        df = df.sort_values('Date')
        df['Date'] = df['Date'].dt.strftime('%Y-%m-%d')
        
        return f"Timeline built with {len(events)} events.", df
        
    except Exception as e:
        return f"Error building timeline: {str(e)}", pd.DataFrame()


def detect_rico_patterns(query: str):
    """Detect potential RICO-related patterns"""
    if not query or not query.strip():
        return "Please enter a query to analyze for RICO patterns.", ""
    
    try:
        # Search for relevant documents
        results = knowledge_base.semantic_search(query, top_k=15)
        
        # Use AI analyzer to detect RICO patterns
        analysis = ai_analyzer.detect_rico_patterns(
            query=query,
            documents=results
        )
        
        return analysis
        
    except Exception as e:
        return f"Error detecting RICO patterns: {str(e)}", ""


def generate_summary(doc_ids: List[str], summary_type: str = "general"):
    """Generate summaries of selected documents"""
    if not doc_ids:
        return "Please select documents to summarize.", ""
    
    try:
        documents = []
        for doc_id in doc_ids:
            doc = knowledge_base.get_document(doc_id)
            if doc:
                documents.append(doc)
        
        if not documents:
            return "No documents found for selected IDs.", ""
        
        summary = ai_analyzer.generate_summary(
            documents=documents,
            summary_type=summary_type
        )
        
        return summary
        
    except Exception as e:
        return f"Error generating summary: {str(e)}", ""


def find_contradictions(query: str):
    """Find documents that contradict each other"""
    if not query or not query.strip():
        return "Please enter a query to find contradictions.", ""
    
    try:
        results = knowledge_base.semantic_search(query, top_k=10)
        
        contradictions = ai_analyzer.find_contradictions(
            query=query,
            documents=results
        )
        
        return contradictions
        
    except Exception as e:
        return f"Error finding contradictions: {str(e)}", ""


def analyze_relationships(entities: str):
    """Analyze relationships between entities"""
    if not entities or not entities.strip():
        return "Please enter entities to analyze (comma-separated).", ""
    
    try:
        entity_list = [e.strip() for e in entities.split(',')]
        
        # Search for documents mentioning these entities
        all_results = []
        for entity in entity_list:
            results = knowledge_base.semantic_search(entity, top_k=5)
            all_results.extend(results)
        
        # Analyze relationships
        relationships = ai_analyzer.analyze_relationships(
            entities=entity_list,
            documents=all_results
        )
        
        return relationships
        
    except Exception as e:
        return f"Error analyzing relationships: {str(e)}", ""


# Create Gradio Interface
with gr.Blocks(title="Private AI Litigation Knowledge System") as demo:
    gr.Markdown(f"""
    # ⚖️ Private AI Litigation Knowledge System
    
    A comprehensive, secure AI assistant to organize, analyze, and support factual development 
    for multiple overlapping legal cases (state, federal, bankruptcy, business/financial).
    
    **Features:**
    - 📄 Document ingestion and processing (emails, PDFs, court filings, notes, evidence, financial records)
    - 🧠 Intelligent knowledge base with semantic search
    - 🔍 Advanced query and analysis capabilities
    - 📅 Chronological timeline builder
    - 🎯 RICO pattern detection
    - 📊 Relationship analysis and contradiction detection
    
    **Storage Locations:**
    - 📁 **Original Documents:** `{DOCUMENTS_STORAGE_DIR.absolute()}`
    - 🧠 **Knowledge Base:** `{knowledge_base.storage_dir.absolute()}`
    """)
    
    with gr.Tabs() as main_tabs:
        # Tab 1: Document Upload & Management
        with gr.Tab("📁 Document Upload"):
            gr.Markdown("### Upload and Process Legal Documents")
            gr.Markdown("Upload emails, PDFs, court filings, notes, evidence, and financial records. "
                       "Documents are automatically classified and organized.")
            
            with gr.Row():
                with gr.Column(scale=2):
                    file_upload = gr.File(
                        label="Upload Documents",
                        file_count="multiple",
                        file_types=[".pdf", ".txt", ".doc", ".docx", ".eml", ".msg", ".csv", ".xlsx"],
                        height=200
                    )
                    upload_btn = gr.Button("Process Documents", variant="primary", size="lg")
                
                with gr.Column(scale=1):
                    gr.Markdown("**Supported Formats:**")
                    gr.Markdown("""
                    - PDF documents
                    - Text files (.txt)
                    - Word documents (.doc, .docx)
                    - Email files (.eml, .msg)
                    - Spreadsheets (.csv, .xlsx)
                    """)
            
            with gr.Row():
                upload_status = gr.Textbox(
                    label="Processing Status",
                    lines=10,
                    interactive=False
                )
            
            with gr.Row():
                documents_table = gr.Dataframe(
                    label="Uploaded Documents",
                    headers=["File Name", "Type", "Status"],
                    interactive=False,
                    wrap=True
                )
            
            upload_btn.click(
                fn=process_uploaded_files,
                inputs=file_upload,
                outputs=[upload_status, documents_table]
            )
            file_upload.upload(
                fn=process_uploaded_files,
                inputs=file_upload,
                outputs=[upload_status, documents_table]
            )
            
            # Google Drive Integration Section
            if google_drive:
                gr.Markdown("---")
                gr.Markdown("### 📥 Import from Google Drive")
                gr.Markdown("Import documents directly from your Google Drive. "
                           "Files will be downloaded and processed automatically.")
                
                with gr.Row():
                    with gr.Column():
                        drive_folder_id = gr.Textbox(
                            label="Google Drive Folder ID (Optional)",
                            placeholder="Leave empty to import all accessible files, or enter a specific folder ID",
                            value=Config.GOOGLE_DRIVE_FOLDER_ID if Config else None
                        )
                        list_drive_btn = gr.Button("List Files in Google Drive", variant="secondary")
                        import_drive_btn = gr.Button("Import from Google Drive", variant="primary")
                
                with gr.Row():
                    drive_files_list = gr.Dataframe(
                        label="Files Available in Google Drive",
                        headers=["File Name", "Type", "Size", "Modified"],
                        interactive=False,
                        wrap=True
                    )
                
                with gr.Row():
                    drive_import_status = gr.Textbox(
                        label="Google Drive Import Status",
                        lines=10,
                        interactive=False
                    )
                
                list_drive_btn.click(
                    fn=list_google_drive_files,
                    inputs=drive_folder_id,
                    outputs=[drive_import_status, drive_files_list]
                )
                
                import_drive_btn.click(
                    fn=import_from_google_drive,
                    inputs=drive_folder_id,
                    outputs=[drive_import_status, documents_table]
                )
        
        # Tab 2: Knowledge Base Query
        with gr.Tab("🔍 Search & Query"):
            gr.Markdown("### Query Your Legal Knowledge Base")
            gr.Markdown("Ask questions and search through all uploaded documents using semantic search.")
            
            with gr.Row():
                with gr.Column():
                    query_input = gr.Textbox(
                        label="Enter your query",
                        placeholder="e.g., What events involve these three people?",
                        lines=3
                    )
                    search_type = gr.Radio(
                        choices=["semantic", "keyword", "hybrid"],
                        value="semantic",
                        label="Search Type"
                    )
                    search_btn = gr.Button("Search", variant="primary")
                
            with gr.Row():
                with gr.Column():
                    search_results = gr.Markdown(label="Search Results")
                    sources_list = gr.Textbox(
                        label="Source Documents",
                        lines=5,
                        interactive=False
                    )
            
            search_btn.click(
                fn=query_knowledge_base,
                inputs=[query_input, search_type],
                outputs=[search_results, sources_list]
            )
            query_input.submit(
                fn=query_knowledge_base,
                inputs=[query_input, search_type],
                outputs=[search_results, sources_list]
            )
        
        # Tab 3: AI Assistant Chat
        with gr.Tab("💬 AI Assistant"):
            gr.Markdown("### Interactive AI Assistant")
            gr.Markdown("Ask complex questions about your legal documents. The AI will analyze "
                       "all relevant materials and provide comprehensive answers.")
            
            gr.ChatInterface(
                fn=ask_question,
                title="Legal Document Assistant",
                description="Ask questions about your legal documents, cases, and evidence.",
                examples=[
                    "What events involve these three people?",
                    "Summarize filings related to this issue.",
                    "Are there documents that contradict each other?",
                    "Build a timeline of financial or transactional events.",
                    "Show possible RICO-pattern connections around these dates."
                ],
                cache_examples=False
            )
        
        # Tab 4: Timeline Builder
        with gr.Tab("📅 Timeline Builder"):
            gr.Markdown("### Build Chronological Timelines")
            gr.Markdown("Create chronological timelines of events from your documents.")
            
            with gr.Row():
                with gr.Column():
                    timeline_query = gr.Textbox(
                        label="Query for Timeline",
                        placeholder="e.g., financial transactions, communications, court filings",
                        lines=2
                    )
                    timeline_btn = gr.Button("Build Timeline", variant="primary")
                
            with gr.Row():
                timeline_status = gr.Textbox(
                    label="Status",
                    interactive=False
                )
            
            with gr.Row():
                timeline_df = gr.Dataframe(
                    label="Timeline Events",
                    interactive=False,
                    wrap=True
                )
            
            timeline_btn.click(
                fn=build_timeline,
                inputs=timeline_query,
                outputs=[timeline_status, timeline_df]
            )
            timeline_query.submit(
                fn=build_timeline,
                inputs=timeline_query,
                outputs=[timeline_status, timeline_df]
            )
        
        # Tab 5: RICO Pattern Detection
        with gr.Tab("🎯 RICO Analysis"):
            gr.Markdown("### RICO Pattern Detection")
            gr.Markdown("Identify potential RICO-related patterns including actors, timing, "
                       "coordination, transactions, and communications.")
            
            with gr.Row():
                with gr.Column():
                    rico_query = gr.Textbox(
                        label="Query for RICO Analysis",
                        placeholder="e.g., transactions between parties, coordinated actions",
                        lines=3
                    )
                    rico_btn = gr.Button("Analyze for RICO Patterns", variant="primary")
                
            with gr.Row():
                rico_analysis = gr.Markdown(label="RICO Pattern Analysis")
            
            rico_btn.click(
                fn=detect_rico_patterns,
                inputs=rico_query,
                outputs=rico_analysis
            )
            rico_query.submit(
                fn=detect_rico_patterns,
                inputs=rico_query,
                outputs=rico_analysis
            )
        
        # Tab 6: Analysis Tools
        with gr.Tab("📊 Analysis Tools"):
            gr.Markdown("### Advanced Analysis Tools")
            
            with gr.Tabs() as analysis_tabs:
                with gr.Tab("Summaries"):
                    gr.Markdown("### Generate Document Summaries")
                    doc_ids_input = gr.Textbox(
                        label="Document IDs (comma-separated)",
                        placeholder="doc1, doc2, doc3"
                    )
                    summary_type = gr.Radio(
                        choices=["general", "detailed", "executive"],
                        value="general",
                        label="Summary Type"
                    )
                    summary_btn = gr.Button("Generate Summary", variant="primary")
                    summary_output = gr.Markdown(label="Summary")
                    
                    summary_btn.click(
                        fn=lambda ids, stype: generate_summary(
                            [d.strip() for d in ids.split(',')] if ids else [],
                            stype
                        ),
                        inputs=[doc_ids_input, summary_type],
                        outputs=summary_output
                    )
                
                with gr.Tab("Contradictions"):
                    gr.Markdown("### Find Contradictory Documents")
                    contradiction_query = gr.Textbox(
                        label="Query",
                        placeholder="e.g., statements about the same event",
                        lines=2
                    )
                    contradiction_btn = gr.Button("Find Contradictions", variant="primary")
                    contradiction_output = gr.Markdown(label="Contradictions Found")
                    
                    contradiction_btn.click(
                        fn=find_contradictions,
                        inputs=contradiction_query,
                        outputs=contradiction_output
                    )
                
                with gr.Tab("Relationships"):
                    gr.Markdown("### Analyze Entity Relationships")
                    entities_input = gr.Textbox(
                        label="Entities (comma-separated)",
                        placeholder="Person A, Person B, Company C",
                        lines=2
                    )
                    relationship_btn = gr.Button("Analyze Relationships", variant="primary")
                    relationship_output = gr.Markdown(label="Relationship Analysis")
                    
                    relationship_btn.click(
                        fn=analyze_relationships,
                        inputs=entities_input,
                        outputs=relationship_output
                    )
    
    gr.Markdown("---")
    gr.Markdown(f"""
    ### 🔒 Privacy & Security
    - All documents are processed locally
    - No data is sent to external services
    - Your knowledge base remains private and secure
    
    ### 📁 File Storage
    - **Original files saved to:** `{DOCUMENTS_STORAGE_DIR.absolute()}`
    - **Knowledge base data:** `{knowledge_base.storage_dir.absolute()}`
    - Files are permanently stored and will not be deleted automatically
    """)

if __name__ == "__main__":
    print("\n" + "="*60)
    print("Starting Private AI Litigation Knowledge System")
    print("="*60)
    
    # Get configuration values
    if Config:
        Config.print_config_summary()
        server_name = Config.SERVER_NAME
        server_port = Config.SERVER_PORT
        share = Config.SHARE
        auth_tuple = Config.get_auth_tuple()
    else:
        server_name = "127.0.0.1"
        server_port = 7860
        share = False
        auth_tuple = None
        print("⚠ Running with default configuration (no config module)")
    
    print(f"\n✓ Server starting on http://{server_name}:{server_port}")
    if server_name == "127.0.0.1":
        print(f"✓ Also accessible at http://localhost:{server_port}")
        print(f"\n⚠ IMPORTANT: Use http://localhost:{server_port} or http://127.0.0.1:{server_port}")
        print("   Do NOT use http://0.0.0.0:{server_port} in your browser")
    if auth_tuple:
        print(f"\n🔒 Authentication ENABLED - Login required to access the system")
    else:
        print(f"\n⚠ Authentication DISABLED - System is open to anyone")
        print("   Set AUTH_ENABLED=true in .env file to enable authentication")
    print("\n" + "="*60 + "\n")
    
    demo.launch(
        share=share, 
        server_name=server_name, 
        auth=auth_tuple,  # Will be None if auth is disabled
        server_port=server_port, 
        theme=gr.themes.Soft(),
        pwa=True,
        footer_links=[""]
    )

