# 📁 File Storage Explanation

## Where Your Documents Are Stored

When you upload documents through the Litigation Knowledge System, they are saved in **two locations**:

### 1. 📄 Original Documents (`./uploaded_documents/`)

**Location:** `C:\Users\Administrator\Documents\Pink\gradio\uploaded_documents\`

**What's stored here:**
- **Original uploaded files** (PDFs, emails, Word docs, etc.)
- Files are saved with timestamps to avoid conflicts
- Example: `contract_20241219_143022.pdf`

**Why this matters:**
- Your original files are **permanently saved**
- They won't be deleted automatically
- You can access them directly from your file system
- Files are organized in one place

### 2. 🧠 Knowledge Base (`./knowledge_base/`)

**Location:** `C:\Users\Administrator\Documents\Pink\gradio\knowledge_base\`

**What's stored here:**
- **Extracted text content** from your documents
- **Metadata** (parties, dates, topics, document types)
- **Vector embeddings** for semantic search (`embeddings.npy`)
- **Search index** (`index.faiss`)
- **Metadata file** (`metadata.json`)

**Why this matters:**
- This is what powers the search and AI features
- Contains processed/analyzed data, not original files
- Much smaller than original files (text only)

## How It Works

1. **You upload a file** → Gradio temporarily stores it in its cache
2. **System processes it** → Extracts text, metadata, etc.
3. **Original file is copied** → Saved to `uploaded_documents/` with timestamp
4. **Content is indexed** → Stored in `knowledge_base/` for search
5. **You can search/query** → Uses the knowledge base, not original files

## Finding Your Files

### Method 1: Check the UI
- The main page shows storage locations
- Upload status shows where each file was saved

### Method 2: File Explorer
1. Navigate to: `C:\Users\Administrator\Documents\Pink\gradio\`
2. Open the `uploaded_documents` folder
3. All your uploaded files are there!

### Method 3: Check Terminal Output
When you upload files, the status message shows:
```
✓ document.pdf - pdf_document processed successfully
  📁 Saved to: C:\Users\Administrator\Documents\Pink\gradio\uploaded_documents\document_20241219_143022.pdf
```

## Important Notes

⚠️ **Gradio Temporary Files:**
- Gradio also stores files temporarily in: `%TEMP%\gradio\` (Windows) or `/tmp/gradio` (Linux)
- These are **temporary** and may be cleaned up
- **Your files are safe** because we copy them to `uploaded_documents/`

✅ **Permanent Storage:**
- Files in `uploaded_documents/` are **permanent**
- They won't be deleted unless you delete them manually
- You can backup this folder to keep your documents safe

## Backup Recommendations

To backup your litigation system:

1. **Backup original documents:**
   ```
   Copy: uploaded_documents/ folder
   ```

2. **Backup knowledge base:**
   ```
   Copy: knowledge_base/ folder
   ```

3. **Both contain important data:**
   - `uploaded_documents/` = Your original files
   - `knowledge_base/` = Searchable index and metadata

## Changing Storage Location

If you want to change where files are stored, edit `litigation_system.py`:

```python
# Line ~27
DOCUMENTS_STORAGE_DIR = Path("./uploaded_documents")  # Change this path
```

Or for knowledge base:

```python
# In knowledge_base.py, line ~30
def __init__(self, storage_dir: str = "./knowledge_base"):  # Change this
```

## Questions?

- **Q: Can I delete files from `uploaded_documents/`?**
  - A: Yes, but you'll lose access to the original file. The knowledge base will still have the text content.

- **Q: Can I move files to a different location?**
  - A: Yes, but update the paths in the code, or the system won't find them.

- **Q: How much space do I need?**
  - A: Original files take their normal size. Knowledge base is usually much smaller (text + embeddings).

