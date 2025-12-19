"""
AI Analyzer Module
Provides AI-powered analysis capabilities including RICO pattern detection,
contradiction finding, relationship analysis, and summarization.
"""

import re
from typing import List, Dict, Any, Optional
from datetime import datetime


class AIAnalyzer:
    """AI-powered analysis for legal documents"""
    
    def __init__(self):
        self.rico_keywords = [
            'enterprise', 'pattern', 'racketeering', 'conspiracy',
            'coordination', 'scheme', 'fraud', 'transaction',
            'communication', 'timing', 'actor', 'participant'
        ]
    
    def answer_question(self, question: str, knowledge_base, chat_history: List = None) -> str:
        """Generate comprehensive answer to a question based on knowledge base"""
        if chat_history is None:
            chat_history = []
        
        # Search knowledge base for relevant documents
        results = knowledge_base.semantic_search(question, top_k=5)
        
        if not results:
            return "I couldn't find any relevant documents to answer your question. Please upload documents first."
        
        # Build context from search results
        context_parts = []
        for i, result in enumerate(results, 1):
            doc_info = result.get('metadata', {})
            content = result.get('content', '')
            # Truncate long content
            if len(content) > 1000:
                content = content[:1000] + "..."
            
            context_parts.append(
                f"Document {i}: {doc_info.get('file_name', 'Unknown')}\n"
                f"Type: {doc_info.get('doc_type', 'Unknown')}\n"
                f"Content: {content}\n"
            )
        
        context = "\n".join(context_parts)
        
        # Generate answer (simplified - in production, use an LLM)
        answer = f"""Based on the documents in the knowledge base, here's what I found:

**Question:** {question}

**Relevant Documents Found:** {len(results)}

**Answer:**
"""
        
        # Extract key information from context
        if 'timeline' in question.lower() or 'when' in question.lower():
            dates = self._extract_dates_from_context(context)
            if dates:
                answer += f"\n**Key Dates Found:**\n"
                for date in dates[:10]:
                    answer += f"- {date}\n"
        
        if 'who' in question.lower() or 'people' in question.lower() or 'parties' in question.lower():
            parties = self._extract_parties_from_context(context)
            if parties:
                answer += f"\n**Parties/People Mentioned:**\n"
                for party in parties[:10]:
                    answer += f"- {party}\n"
        
        # Add summary of relevant content
        answer += f"\n**Summary:**\n"
        answer += self._summarize_context(context, question)
        
        answer += f"\n\n**Source Documents:**\n"
        for i, result in enumerate(results, 1):
            doc_info = result.get('metadata', {})
            answer += f"{i}. {doc_info.get('file_name', 'Unknown')} (Relevance: {result.get('score', 0):.3f})\n"
        
        return answer
    
    def detect_rico_patterns(self, query: str, documents: List[Dict[str, Any]]) -> str:
        """Detect potential RICO-related patterns"""
        if not documents:
            return "No documents found for RICO analysis."
        
        analysis = f"""# RICO Pattern Analysis

**Query:** {query}

**Documents Analyzed:** {len(documents)}

## Potential RICO Elements Detected:

"""
        
        # Analyze for RICO elements
        enterprise_indicators = []
        pattern_indicators = []
        coordination_indicators = []
        transaction_indicators = []
        communication_indicators = []
        
        for doc in documents:
            content = doc.get('content', '').lower()
            metadata = doc.get('metadata', {})
            file_name = metadata.get('file_name', 'Unknown')
            
            # Check for enterprise indicators
            if any(keyword in content for keyword in ['enterprise', 'organization', 'entity', 'business', 'company']):
                enterprise_indicators.append(file_name)
            
            # Check for pattern indicators
            if any(keyword in content for keyword in ['pattern', 'repeated', 'systematic', 'ongoing']):
                pattern_indicators.append(file_name)
            
            # Check for coordination indicators
            if any(keyword in content for keyword in ['coordinate', 'conspire', 'collaborate', 'together', 'joint']):
                coordination_indicators.append(file_name)
            
            # Check for transaction indicators
            if any(keyword in content for keyword in ['transaction', 'payment', 'transfer', 'exchange', 'deal']):
                transaction_indicators.append(file_name)
            
            # Check for communication indicators
            if any(keyword in content for keyword in ['email', 'communication', 'message', 'call', 'meeting', 'discuss']):
                communication_indicators.append(file_name)
        
        # Build analysis report
        if enterprise_indicators:
            analysis += f"### Enterprise Indicators\n"
            analysis += f"Found in {len(set(enterprise_indicators))} document(s):\n"
            for doc in set(enterprise_indicators)[:5]:
                analysis += f"- {doc}\n"
            analysis += "\n"
        
        if pattern_indicators:
            analysis += f"### Pattern of Activity Indicators\n"
            analysis += f"Found in {len(set(pattern_indicators))} document(s):\n"
            for doc in set(pattern_indicators)[:5]:
                analysis += f"- {doc}\n"
            analysis += "\n"
        
        if coordination_indicators:
            analysis += f"### Coordination Indicators\n"
            analysis += f"Found in {len(set(coordination_indicators))} document(s):\n"
            for doc in set(coordination_indicators)[:5]:
                analysis += f"- {doc}\n"
            analysis += "\n"
        
        if transaction_indicators:
            analysis += f"### Transaction Indicators\n"
            analysis += f"Found in {len(set(transaction_indicators))} document(s):\n"
            for doc in set(transaction_indicators)[:5]:
                analysis += f"- {doc}\n"
            analysis += "\n"
        
        if communication_indicators:
            analysis += f"### Communication Indicators\n"
            analysis += f"Found in {len(set(communication_indicators))} document(s):\n"
            for doc in set(communication_indicators)[:5]:
                analysis += f"- {doc}\n"
            analysis += "\n"
        
        # Extract dates for timeline analysis
        all_dates = []
        for doc in documents:
            metadata = doc.get('metadata', {})
            dates = metadata.get('dates', [])
            all_dates.extend(dates)
        
        if all_dates:
            analysis += f"### Timeline Analysis\n"
            analysis += f"Found {len(set(all_dates))} unique dates across documents.\n"
            analysis += f"Date range: {min(set(all_dates))} to {max(set(all_dates))}\n"
            analysis += "\n"
        
        # Recommendations
        analysis += f"## Recommendations\n"
        analysis += f"- Review documents with multiple RICO indicators for detailed analysis\n"
        analysis += f"- Build detailed timeline of events involving identified parties\n"
        analysis += f"- Examine communications and transactions for coordination patterns\n"
        analysis += f"- Look for repeated patterns of activity over time\n"
        
        return analysis
    
    def find_contradictions(self, query: str, documents: List[Dict[str, Any]]) -> str:
        """Find contradictory statements in documents"""
        if not documents:
            return "No documents found for contradiction analysis."
        
        analysis = f"""# Contradiction Analysis

**Query:** {query}

**Documents Analyzed:** {len(documents)}

## Potential Contradictions:

"""
        
        # Simple contradiction detection based on keyword analysis
        # In production, use more sophisticated NLP techniques
        
        contradictions = []
        
        # Extract key facts from each document
        facts = []
        for doc in documents:
            content = doc.get('content', '')
            metadata = doc.get('metadata', {})
            file_name = metadata.get('file_name', 'Unknown')
            
            # Extract statements (simplified)
            sentences = re.split(r'[.!?]+', content)
            for sentence in sentences[:20]:  # Limit to first 20 sentences
                if len(sentence.strip()) > 20:  # Only meaningful sentences
                    facts.append({
                        'statement': sentence.strip(),
                        'source': file_name,
                        'content': content[:500]
                    })
        
        # Look for contradictory patterns (simplified)
        # In production, use semantic similarity and contradiction detection models
        
        if len(facts) > 1:
            analysis += f"Analyzed {len(facts)} statements across {len(documents)} documents.\n\n"
            analysis += "**Note:** This is a simplified analysis. For comprehensive contradiction detection, "
            analysis += "consider using advanced NLP models that can detect semantic contradictions.\n\n"
            
            # Group by source
            by_source = {}
            for fact in facts:
                source = fact['source']
                if source not in by_source:
                    by_source[source] = []
                by_source[source].append(fact['statement'])
            
            analysis += "**Statements by Document:**\n"
            for source, statements in list(by_source.items())[:5]:
                analysis += f"\n**{source}:**\n"
                for stmt in statements[:3]:
                    analysis += f"- {stmt[:200]}...\n"
        
        return analysis
    
    def analyze_relationships(self, entities: List[str], documents: List[Dict[str, Any]]) -> str:
        """Analyze relationships between entities"""
        if not entities or not documents:
            return "Please provide entities and ensure documents are available."
        
        analysis = f"""# Relationship Analysis

**Entities:** {', '.join(entities)}

**Documents Analyzed:** {len(documents)}

## Relationships Found:

"""
        
        # Find co-occurrences
        relationships = {}
        
        for doc in documents:
            content = doc.get('content', '')
            metadata = doc.get('metadata', {})
            file_name = metadata.get('file_name', 'Unknown')
            
            # Find which entities are mentioned together
            mentioned_entities = [e for e in entities if e.lower() in content.lower()]
            
            if len(mentioned_entities) > 1:
                # Create relationship pairs
                for i, entity1 in enumerate(mentioned_entities):
                    for entity2 in mentioned_entities[i+1:]:
                        pair = tuple(sorted([entity1, entity2]))
                        if pair not in relationships:
                            relationships[pair] = []
                        relationships[pair].append(file_name)
        
        if relationships:
            for (entity1, entity2), docs in relationships.items():
                analysis += f"### {entity1} ↔ {entity2}\n"
                analysis += f"**Co-occurrences:** {len(docs)} document(s)\n"
                analysis += f"**Documents:**\n"
                for doc in set(docs)[:5]:
                    analysis += f"- {doc}\n"
                analysis += "\n"
        else:
            analysis += "No direct relationships found between the specified entities in the analyzed documents.\n"
        
        # Extract dates for timeline
        all_dates = []
        for doc in documents:
            metadata = doc.get('metadata', {})
            dates = metadata.get('dates', [])
            all_dates.extend(dates)
        
        if all_dates:
            analysis += f"\n## Timeline Context\n"
            analysis += f"Found {len(set(all_dates))} unique dates in related documents.\n"
        
        return analysis
    
    def generate_summary(self, documents: List[Dict[str, Any]], summary_type: str = "general") -> str:
        """Generate summary of documents"""
        if not documents:
            return "No documents provided for summarization."
        
        summary = f"""# Document Summary

**Summary Type:** {summary_type.title()}
**Documents Summarized:** {len(documents)}

"""
        
        if summary_type == "executive":
            summary += "## Executive Summary\n\n"
            summary += "Key points from the documents:\n\n"
        elif summary_type == "detailed":
            summary += "## Detailed Summary\n\n"
        else:
            summary += "## General Summary\n\n"
        
        # Summarize each document
        for i, doc in enumerate(documents, 1):
            content = doc.get('content', '')
            metadata = doc.get('metadata', {})
            file_name = metadata.get('file_name', 'Unknown')
            doc_type = metadata.get('doc_type', 'Unknown')
            
            summary += f"### Document {i}: {file_name}\n"
            summary += f"**Type:** {doc_type}\n\n"
            
            # Extract key information
            if summary_type == "executive":
                # Very brief summary
                summary += f"{content[:200]}...\n\n"
            elif summary_type == "detailed":
                # More detailed summary
                summary += f"{content[:1000]}...\n\n"
            else:
                # General summary
                summary += f"{content[:500]}...\n\n"
        
        # Overall summary
        summary += "\n## Overall Summary\n\n"
        summary += f"Analyzed {len(documents)} document(s) covering various aspects of the case. "
        summary += "Key themes and information have been extracted and organized above.\n"
        
        return summary
    
    def _extract_dates_from_context(self, context: str) -> List[str]:
        """Extract dates from context"""
        date_patterns = [
            r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}',
            r'\d{4}[/-]\d{1,2}[/-]\d{1,2}',
            r'(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}',
        ]
        
        dates = []
        for pattern in date_patterns:
            dates.extend(re.findall(pattern, context))
        
        return list(set(dates))[:20]
    
    def _extract_parties_from_context(self, context: str) -> List[str]:
        """Extract parties/people from context"""
        # Simple pattern matching
        patterns = [
            r'(?:Plaintiff|Defendant|Appellant|Appellee|Petitioner|Respondent)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
            r'([A-Z][a-z]+\s+[A-Z][a-z]+)\s+v\.',
            r'(?:Mr\.|Ms\.|Mrs\.|Dr\.)\s+([A-Z][a-z]+\s+[A-Z][a-z]+)',
        ]
        
        parties = []
        for pattern in patterns:
            matches = re.findall(pattern, context)
            if matches:
                if isinstance(matches[0], tuple):
                    parties.extend([m for match in matches for m in match if m])
                else:
                    parties.extend(matches)
        
        return list(set(parties))[:15]
    
    def _summarize_context(self, context: str, question: str) -> str:
        """Generate a summary of the context relevant to the question"""
        # Simplified summarization
        # In production, use an LLM for better summarization
        
        sentences = re.split(r'[.!?]+', context)
        relevant_sentences = []
        
        question_terms = question.lower().split()
        
        for sentence in sentences:
            sentence_lower = sentence.lower()
            # Count how many question terms appear in sentence
            matches = sum(1 for term in question_terms if term in sentence_lower)
            if matches > 0 and len(sentence.strip()) > 20:
                relevant_sentences.append(sentence.strip())
        
        if relevant_sentences:
            return " ".join(relevant_sentences[:5])
        else:
            return context[:500] + "..." if len(context) > 500 else context

