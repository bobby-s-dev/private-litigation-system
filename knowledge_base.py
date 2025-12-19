"""
Knowledge Base Module
Manages document storage, indexing, and retrieval using vector embeddings.
"""

import os
import json
import hashlib
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path
import numpy as np

try:
    from sentence_transformers import SentenceTransformer
    EMBEDDINGS_AVAILABLE = True
except ImportError:
    EMBEDDINGS_AVAILABLE = False

try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False


class KnowledgeBase:
    """Knowledge base with vector storage and semantic search"""
    
    def __init__(self, storage_dir: str = "./knowledge_base"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)
        
        self.documents = {}
        self.metadata_file = self.storage_dir / "metadata.json"
        self.embeddings_file = self.storage_dir / "embeddings.npy"
        self.index_file = self.storage_dir / "index.faiss"
        
        # Initialize embeddings model
        if EMBEDDINGS_AVAILABLE:
            try:
                self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
                self.embedding_dim = 384
            except Exception as e:
                print(f"Warning: Could not load embedding model: {e}")
                self.embedding_model = None
                self.embedding_dim = 384
        else:
            self.embedding_model = None
            self.embedding_dim = 384
        
        # Initialize FAISS index
        self.index = None
        self.embeddings = []
        self.doc_ids = []
        
        # Load existing data
        self._load_data()
    
    def _load_data(self):
        """Load existing documents and index"""
        # Load metadata
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r') as f:
                    self.documents = json.load(f)
            except Exception as e:
                print(f"Warning: Could not load metadata: {e}")
                self.documents = {}
        
        # Load embeddings and index
        if FAISS_AVAILABLE and self.embeddings_file.exists() and self.index_file.exists():
            try:
                self.embeddings = np.load(self.embeddings_file)
                self.index = faiss.read_index(str(self.index_file))
                
                # Reconstruct doc_ids from metadata
                self.doc_ids = list(self.documents.keys())
            except Exception as e:
                print(f"Warning: Could not load index: {e}")
                self.embeddings = []
                self.index = None
                self.doc_ids = []
    
    def _save_data(self):
        """Save documents and index to disk"""
        # Save metadata
        try:
            with open(self.metadata_file, 'w') as f:
                json.dump(self.documents, f, indent=2)
        except Exception as e:
            print(f"Error saving metadata: {e}")
        
        # Save embeddings and index
        if FAISS_AVAILABLE and len(self.embeddings) > 0:
            try:
                np.save(self.embeddings_file, np.array(self.embeddings))
                if self.index is not None:
                    faiss.write_index(self.index, str(self.index_file))
            except Exception as e:
                print(f"Error saving index: {e}")
    
    def _generate_doc_id(self, content: str, metadata: Dict) -> str:
        """Generate unique document ID"""
        unique_string = f"{content[:100]}{metadata.get('file_name', '')}{datetime.now().isoformat()}"
        return hashlib.md5(unique_string.encode()).hexdigest()
    
    def _get_embedding(self, text: str) -> np.ndarray:
        """Get embedding for text"""
        if self.embedding_model:
            try:
                return self.embedding_model.encode(text, convert_to_numpy=True)
            except Exception as e:
                print(f"Error generating embedding: {e}")
        
        # Fallback: simple hash-based embedding
        hash_obj = hashlib.sha256(text.encode())
        hash_bytes = hash_obj.digest()
        # Use first embedding_dim bytes and pad if needed
        embedding = np.frombuffer(hash_bytes[:self.embedding_dim], dtype=np.float32)
        if len(embedding) < self.embedding_dim:
            padding = np.zeros(self.embedding_dim - len(embedding), dtype=np.float32)
            embedding = np.concatenate([embedding, padding])
        return embedding[:self.embedding_dim]
    
    def add_document(self, content: str, metadata: Dict[str, Any]) -> str:
        """Add a document to the knowledge base"""
        doc_id = self._generate_doc_id(content, metadata)
        
        # Store document
        self.documents[doc_id] = {
            'content': content,
            'metadata': metadata,
            'added_date': datetime.now().isoformat()
        }
        
        # Generate embedding
        embedding = self._get_embedding(content)
        self.embeddings.append(embedding)
        self.doc_ids.append(doc_id)
        
        # Update FAISS index
        if FAISS_AVAILABLE:
            if self.index is None:
                self.index = faiss.IndexFlatL2(self.embedding_dim)
            
            # Add to index
            embedding_2d = embedding.reshape(1, -1).astype('float32')
            self.index.add(embedding_2d)
        else:
            # Simple list-based storage
            pass
        
        # Save to disk
        self._save_data()
        
        return doc_id
    
    def get_document(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a document by ID"""
        return self.documents.get(doc_id)
    
    def semantic_search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Perform semantic search using vector similarity"""
        if len(self.documents) == 0:
            return []
        
        # Get query embedding
        query_embedding = self._get_embedding(query)
        
        if FAISS_AVAILABLE and self.index is not None:
            # Use FAISS for fast search
            query_embedding_2d = query_embedding.reshape(1, -1).astype('float32')
            distances, indices = self.index.search(query_embedding_2d, min(top_k, len(self.doc_ids)))
            
            results = []
            for i, idx in enumerate(indices[0]):
                if idx < len(self.doc_ids):
                    doc_id = self.doc_ids[idx]
                    doc = self.documents[doc_id]
                    distance = float(distances[0][i])
                    # Convert distance to similarity score (lower distance = higher similarity)
                    score = 1.0 / (1.0 + distance)
                    results.append({
                        'content': doc['content'],
                        'metadata': doc['metadata'],
                        'score': score
                    })
            return results
        else:
            # Fallback: simple cosine similarity
            results = []
            for doc_id, doc in self.documents.items():
                doc_embedding = self._get_embedding(doc['content'])
                # Cosine similarity
                similarity = np.dot(query_embedding, doc_embedding) / (
                    np.linalg.norm(query_embedding) * np.linalg.norm(doc_embedding) + 1e-8
                )
                results.append({
                    'content': doc['content'],
                    'metadata': doc['metadata'],
                    'score': float(similarity)
                })
            
            # Sort by score and return top_k
            results.sort(key=lambda x: x['score'], reverse=True)
            return results[:top_k]
    
    def keyword_search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Perform keyword-based search"""
        if len(self.documents) == 0:
            return []
        
        query_lower = query.lower()
        query_terms = query_lower.split()
        
        results = []
        for doc_id, doc in self.documents.items():
            content_lower = doc['content'].lower()
            # Count matching terms
            matches = sum(1 for term in query_terms if term in content_lower)
            if matches > 0:
                score = matches / len(query_terms) if query_terms else 0
                results.append({
                    'content': doc['content'],
                    'metadata': doc['metadata'],
                    'score': score
                })
        
        # Sort by score
        results.sort(key=lambda x: x['score'], reverse=True)
        return results[:top_k]
    
    def hybrid_search(self, query: str, top_k: int = 5, alpha: float = 0.7) -> List[Dict[str, Any]]:
        """Perform hybrid search combining semantic and keyword search"""
        semantic_results = self.semantic_search(query, top_k * 2)
        keyword_results = self.keyword_search(query, top_k * 2)
        
        # Combine and re-rank
        combined = {}
        for result in semantic_results:
            doc_id = result['metadata'].get('file_name', '')
            if doc_id not in combined:
                combined[doc_id] = result.copy()
                combined[doc_id]['score'] = alpha * result['score']
            else:
                combined[doc_id]['score'] += alpha * result['score']
        
        for result in keyword_results:
            doc_id = result['metadata'].get('file_name', '')
            if doc_id not in combined:
                combined[doc_id] = result.copy()
                combined[doc_id]['score'] = (1 - alpha) * result['score']
            else:
                combined[doc_id]['score'] += (1 - alpha) * result['score']
        
        # Sort by combined score
        results = list(combined.values())
        results.sort(key=lambda x: x['score'], reverse=True)
        return results[:top_k]
    
    def get_all_documents(self) -> List[Dict[str, Any]]:
        """Get all documents in the knowledge base"""
        return list(self.documents.values())
    
    def delete_document(self, doc_id: str) -> bool:
        """Delete a document from the knowledge base"""
        if doc_id in self.documents:
            del self.documents[doc_id]
            
            # Remove from index (simplified - would need proper index management)
            if doc_id in self.doc_ids:
                idx = self.doc_ids.index(doc_id)
                self.doc_ids.pop(idx)
                if len(self.embeddings) > idx:
                    self.embeddings.pop(idx)
            
            self._save_data()
            return True
        return False

