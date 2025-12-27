# Quick Start Guide - Private AI Litigation Knowledge System

## Installation

1. **Install required packages:**
   ```bash
   pip install -r litigation_requirements.txt
   ```

2. **Start the application:**
   ```bash
   python main.py
   ```

3. **Open in browser:**
   - Navigate to `http://localhost:7860`

## First Steps

### 1. Upload Documents
- Go to the **"📁 Document Upload"** tab
- Click "Upload Documents" or drag and drop files
- Supported formats: PDF, TXT, DOC, DOCX, EML, MSG, CSV, XLSX
- Wait for processing to complete (status will show in the status box)

### 2. Search Your Documents
- Go to **"🔍 Search & Query"** tab
- Enter a query like: "What documents mention the settlement?"
- Choose search type (semantic is recommended)
- Click "Search" or press Enter

### 3. Ask Questions
- Go to **"💬 AI Assistant"** tab
- Ask questions in natural language:
  - "What events involve these three people?"
  - "Summarize filings related to this issue."
  - "Are there documents that contradict each other?"

### 4. Build Timelines
- Go to **"📅 Timeline Builder"** tab
- Enter a query like: "financial transactions"
- Click "Build Timeline"
- View chronological events in the table

### 5. RICO Analysis
- Go to **"🎯 RICO Analysis"** tab
- Enter a query related to potential RICO patterns
- Click "Analyze for RICO Patterns"
- Review the analysis report

## Tips

- **Semantic Search** is best for finding documents by meaning
- **Keyword Search** is best for exact term matching
- **Hybrid Search** combines both approaches
- Upload multiple documents at once for better analysis
- The system learns from all uploaded documents

## Troubleshooting

**Documents not processing?**
- Check file format is supported
- Ensure files are not corrupted
- Check console for error messages

**Search not working?**
- Make sure documents have been uploaded
- Try different search types
- Check that sentence-transformers is installed

**Slow performance?**
- Large documents take time to process
- Consider chunking very large files
- Use FAISS GPU version for faster search

## Next Steps

- Read the full README: `README_LITIGATION_SYSTEM.md`
- Customize the system for your needs
- Add more document types if needed
- Integrate with local LLMs for better AI responses

