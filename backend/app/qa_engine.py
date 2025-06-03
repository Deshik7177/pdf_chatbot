from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from typing import List, Tuple
import gc

class SimpleQAEngine:
    def __init__(self):
        # Use a lightweight model for memory efficiency
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.index = None
        self.text_chunks = []
        
    def create_embeddings(self, text_chunks: List[str]) -> np.ndarray:
        """Create embeddings for text chunks"""
        try:
            embeddings = self.model.encode(text_chunks, show_progress_bar=False)
            return embeddings
        except Exception as e:
            raise Exception(f"Error creating embeddings: {str(e)}")
    
    def build_index(self, text_chunks: List[str]):
        """Build FAISS index for similarity search"""
        try:
            self.text_chunks = text_chunks
            embeddings = self.create_embeddings(text_chunks)
            
            # Create FAISS index
            dimension = embeddings.shape[1]
            self.index = faiss.IndexFlatIP(dimension)  # Inner product for cosine similarity
            
            # Normalize embeddings for cosine similarity
            faiss.normalize_L2(embeddings)
            self.index.add(embeddings.astype('float32'))
            
            # Clean up memory
            del embeddings
            gc.collect()
            
        except Exception as e:
            raise Exception(f"Error building index: {str(e)}")
    
    def search_similar_chunks(self, question: str, top_k: int = 3) -> List[Tuple[str, float]]:
        """Search for most similar text chunks"""
        try:
            if self.index is None:
                return []
            
            # Encode question
            question_embedding = self.model.encode([question])
            faiss.normalize_L2(question_embedding)
            
            # Search
            scores, indices = self.index.search(question_embedding.astype('float32'), top_k)
            
            results = []
            for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
                if idx < len(self.text_chunks):
                    results.append((self.text_chunks[idx], float(score)))
            
            return results
        except Exception as e:
            raise Exception(f"Error searching chunks: {str(e)}")
    
    def generate_answer(self, question: str, context_chunks: List[str]) -> str:
        """Generate answer based on context (simple keyword matching approach)"""
        try:
            # Simple approach: find the most relevant chunk and extract relevant sentences
            question_lower = question.lower()
            question_words = set(question_lower.split())
            
            best_chunk = ""
            best_score = 0
            
            for chunk in context_chunks:
                chunk_lower = chunk.lower()
                chunk_words = set(chunk_lower.split())
                
                # Calculate word overlap
                overlap = len(question_words.intersection(chunk_words))
                if overlap > best_score:
                    best_score = overlap
                    best_chunk = chunk
            
            if best_chunk:
                # Extract relevant sentences
                sentences = best_chunk.split('.')
                relevant_sentences = []
                
                for sentence in sentences:
                    sentence_lower = sentence.lower()
                    if any(word in sentence_lower for word in question_words):
                        relevant_sentences.append(sentence.strip())
                
                if relevant_sentences:
                    return '. '.join(relevant_sentences[:3]) + '.'
                else:
                    return best_chunk[:500] + "..." if len(best_chunk) > 500 else best_chunk
            
            return "I couldn't find specific information to answer your question in the document."
            
        except Exception as e:
            return f"Error generating answer: {str(e)}"
    
    def ask_question(self, question: str) -> str:
        """Main method to ask question and get answer"""
        try:
            # Search for relevant chunks
            similar_chunks = self.search_similar_chunks(question, top_k=3)
            
            if not similar_chunks:
                return "No relevant information found in the document."
            
            # Extract text from results
            context_chunks = [chunk for chunk, score in similar_chunks if score > 0.1]
            
            if not context_chunks:
                return "No sufficiently relevant information found in the document."
            
            # Generate answer
            answer = self.generate_answer(question, context_chunks)
            return answer
            
        except Exception as e:
            return f"Error processing question: {str(e)}"