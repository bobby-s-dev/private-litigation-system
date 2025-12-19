"""
Private AI Litigation Knowledge System
A comprehensive, secure AI assistant for organizing, analyzing, and supporting 
factual development for multiple overlapping legal cases.
"""

import gradio as gr
import os
import json
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import pandas as pd

# Import our custom modules
try:
    from document_processor import DocumentProcessor
    from knowledge_base import KnowledgeBase
    from ai_analyzer import AIAnalyzer
    
    # Initialize core components
    doc_processor = DocumentProcessor()
    knowledge_base = KnowledgeBase()
    ai_analyzer = AIAnalyzer()
    
    # Create documents storage directory for permanent file storage
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
    print(f"\n✓ Server starting on http://127.0.0.1:7860")
    print(f"✓ Also accessible at http://localhost:7860")
    print(f"\n⚠ IMPORTANT: Use http://localhost:7860 or http://127.0.0.1:7860")
    print("   Do NOT use http://0.0.0.0:7860 in your browser\n")
    print("="*60 + "\n")
    
    demo.launch(
        share=False, 
        server_name="127.0.0.1", 
        server_port=7860, 
        theme=gr.themes.Soft(),
        pwa=True,
        footer_links=[""]
    )

