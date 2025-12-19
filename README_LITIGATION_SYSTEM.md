# Private AI Litigation Knowledge System

A comprehensive, secure AI assistant built with Gradio to organize, analyze, and support factual development for multiple overlapping legal cases (state, federal, bankruptcy, business/financial).

## Features

### 📄 Document Ingestion Pipeline
- Upload and process multiple document types:
  - PDFs (court filings, contracts, evidence)
  - Emails (.eml, .msg)
  - Word documents (.doc, .docx)
  - Text files (.txt)
  - Financial records (.csv, .xlsx, .xls)
- Automatic document classification
- Metadata extraction (parties, dates, topics)
- Deduplication support

### 🧠 Private AI Knowledge Base
- Secure local storage of all documents
- Vector embeddings for semantic search
- FAISS-based fast similarity search
- Keyword and hybrid search options
- No data sent to external services

### 🔍 Advanced Search & Query
- **Semantic Search**: Find documents by meaning, not just keywords
- **Keyword Search**: Traditional text-based search
- **Hybrid Search**: Combines semantic and keyword search
- **AI Assistant Chat**: Ask complex questions in natural language

### 📅 Timeline Builder
- Build chronological timelines of events
- Extract dates from documents automatically
- Organize events by document type and parties
- Export timeline data

### 🎯 RICO Pattern Detection
- Identify potential RICO-related patterns:
  - Enterprise indicators
  - Pattern of activity
  - Coordination indicators
  - Transaction patterns
  - Communication patterns
- Timeline analysis for RICO cases

### 📊 Analysis Tools
- **Document Summaries**: Generate general, detailed, or executive summaries
- **Contradiction Detection**: Find contradictory statements across documents
- **Relationship Analysis**: Analyze relationships between entities (people, companies)

## Installation

1. **Install Python dependencies:**
   ```bash
   pip install -r litigation_requirements.txt
   ```

2. **Optional: For GPU acceleration (if you have CUDA):**
   ```bash
   pip install faiss-gpu
   ```

## Usage

### Starting the Application

```bash
python litigation_system.py
```

The application will launch at `http://localhost:7860`

### Workflow

1. **Upload Documents** (Tab 1: Document Upload)
   - Click "Upload Documents" or drag and drop files
   - Supported formats: PDF, TXT, DOC, DOCX, EML, MSG, CSV, XLSX
   - Documents are automatically processed and indexed

2. **Search & Query** (Tab 2: Search & Query)
   - Enter your query in natural language
   - Choose search type: semantic, keyword, or hybrid
   - View results with relevance scores and source documents

3. **AI Assistant** (Tab 3: AI Assistant)
   - Ask complex questions about your documents
   - Get comprehensive answers based on all relevant materials
   - Examples:
     - "What events involve these three people?"
     - "Summarize filings related to this issue."
     - "Are there documents that contradict each other?"

4. **Build Timelines** (Tab 4: Timeline Builder)
   - Enter a query to find relevant events
   - System extracts dates and builds chronological timeline
   - View timeline in table format

5. **RICO Analysis** (Tab 5: RICO Analysis)
   - Enter query related to potential RICO patterns
   - System analyzes documents for:
     - Enterprise indicators
     - Coordination patterns
     - Transaction patterns
     - Communication patterns

6. **Analysis Tools** (Tab 6: Analysis Tools)
   - **Summaries**: Generate summaries of selected documents
   - **Contradictions**: Find contradictory statements
   - **Relationships**: Analyze relationships between entities

## System Architecture

```
litigation_system.py          # Main Gradio application
├── document_processor.py     # Document ingestion and processing
├── knowledge_base.py         # Vector storage and retrieval
└── ai_analyzer.py            # AI-powered analysis
```

### Document Processing Flow

1. **Upload** → File received
2. **Extract** → Text content extracted based on file type
3. **Classify** → Document type identified (email, filing, contract, etc.)
4. **Extract Metadata** → Parties, dates, topics extracted
5. **Index** → Content embedded and stored in vector database
6. **Ready** → Document available for search and analysis

### Knowledge Base Storage

- Documents stored in `./knowledge_base/` directory
- Metadata stored as JSON
- Vector embeddings stored as NumPy arrays
- FAISS index for fast similarity search

## Privacy & Security

- ✅ All processing happens locally
- ✅ No data sent to external services
- ✅ Documents stored securely on your machine
- ✅ No cloud dependencies
- ✅ Full control over your data

## Customization

### Adding Custom Document Types

Edit `document_processor.py` to add support for new file types:

```python
def _process_custom_format(self, file_path: str) -> Dict[str, Any]:
    # Your custom processing logic
    return {'content': extracted_text}
```

### Enhancing AI Analysis

Edit `ai_analyzer.py` to:
- Integrate with local LLMs (Ollama, GPT4All, etc.)
- Add custom pattern detection
- Implement advanced contradiction detection

### Improving Search

Edit `knowledge_base.py` to:
- Use different embedding models
- Adjust search parameters
- Add custom ranking algorithms

## Example Queries

### Timeline Queries
- "Build a timeline of financial transactions"
- "Show all events related to the settlement negotiations"
- "Timeline of communications between parties"

### RICO Analysis Queries
- "Analyze transactions for RICO patterns"
- "Find coordination between these parties"
- "Detect RICO patterns around these dates"

### Relationship Queries
- "Analyze relationships between Person A, Person B, and Company C"
- "What is the connection between these entities?"

### General Queries
- "What documents mention both parties?"
- "Find all emails related to the contract"
- "Summarize all court filings"

## Troubleshooting

### PDF Processing Issues
- Ensure PyPDF2 is installed: `pip install PyPDF2`
- Some PDFs may be image-based and require OCR (not included)

### Email Processing Issues
- For .msg files on Windows, consider installing `extract-msg`
- Email attachments are not processed automatically

### Search Not Working
- Ensure documents have been uploaded and processed
- Check that sentence-transformers is installed
- Verify knowledge_base directory exists and has write permissions

### Performance Issues
- Large documents may take time to process
- Consider chunking very large documents
- Use FAISS GPU version for faster search on large datasets

## Future Enhancements

Potential improvements:
- [ ] OCR support for scanned documents
- [ ] Integration with local LLMs (Ollama, GPT4All)
- [ ] Advanced contradiction detection using NLP models
- [ ] Export capabilities (PDF reports, Excel timelines)
- [ ] Multi-user support with authentication
- [ ] Document versioning and change tracking
- [ ] Advanced visualization (network graphs, timeline charts)
- [ ] Integration with legal research databases


