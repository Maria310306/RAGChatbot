from typing import List, Dict, Any
from langchain.prompts import PromptTemplate
from app.utils.vector_store import vector_store_manager
from app.core.config import settings
from app.schemas.chat import ChatRequest


class RAGService:
    def __init__(self):
        # Define prompt templates for different modes
        self.global_rag_prompt = PromptTemplate(
            input_variables=["context", "question"],
            template="""
            You are an assistant helping users understand a published book. 
            Please answer the user's question based ONLY on the provided context.
            If the answer is not in the provided context, say "I cannot answer based on the provided content."
            
            Context: {context}
            
            Question: {question}
            
            Answer:
            """
        )
        
        self.selected_text_prompt = PromptTemplate(
            input_variables=["selected_text", "question"],
            template="""
            You are an assistant helping users understand a published book. 
            Please answer the user's question based ONLY on the selected text provided.
            If the answer is not in the selected text, say "I cannot answer based on the selected text."
            
            Selected Text: {selected_text}
            
            Question: {question}
            
            Answer:
            """
        )

    def generate_response_global(self, query: str, k: int = 4) -> Dict[str, Any]:
        """
        Generate response using global RAG approach (retrieving from entire book content)
        
        Args:
            query: User's question
            k: Number of context chunks to retrieve
            
        Returns:
            Dictionary with response and source information
        """
        # Retrieve relevant documents
        docs = vector_store_manager.similarity_search(query, k=k)
        
        # Combine documents into context
        context = "\n\n".join([doc.page_content for doc in docs])
        
        # Check if context is too long
        if len(context) > settings.MAX_CONTEXT_LENGTH:
            # Truncate context to fit within limits
            context = context[:settings.MAX_CONTEXT_LENGTH]
        
        # If context is empty, return appropriate message
        if not context.strip():
            return {
                "response": "I cannot answer based on the provided content.",
                "sources": []
            }
        
        # For an open-source approach without a local LLM, we'll create a simple 
        # response based on the context that answers the question directly
        response = self._simple_response_generator(query, context)
        
        # Extract sources
        sources = [doc.metadata for doc in docs] if docs else []
        
        return {
            "response": response,
            "sources": sources
        }

    def generate_response_selected_text_only(self, query: str, selected_text: str) -> Dict[str, Any]:
        """
        Generate response using selected text only approach
        
        Args:
            query: User's question
            selected_text: Text that the user has selected/highlighted
            
        Returns:
            Dictionary with response and source information
        """
        # If no selected text is provided, return appropriate message
        if not selected_text.strip():
            return {
                "response": "Selected text is required for 'selected_text_only' mode.",
                "sources": []
            }
        
        # Create response based on the selected text
        response = self._simple_response_generator(query, selected_text)
        
        return {
            "response": response,
            "sources": [{"source": "selected_text", "content": selected_text}]
        }

    def _simple_response_generator(self, query: str, context: str) -> str:
        """
        A simple response generator that tries to answer the query based on the context
        This is a basic implementation without using a language model
        """
        # Convert to lowercase for comparison
        query_lower = query.lower()
        context_lower = context.lower()
        
        # List of common question words to identify the type of question
        question_words = ["what", "who", "when", "where", "why", "how", "which", "whose"]
        
        # Check if the query is a yes/no question
        if query_lower.startswith(("is", "are", "was", "were", "can", "could", "will", "would", "do", "does", "did", "have", "has", "had")):
            # For yes/no questions, check if the context supports a yes or no answer
            if any(word in context_lower for word in ["yes", "true", "correct", "indeed", "certainly", "definitely", "exactly"]):
                return f"Based on the provided content, the answer appears to be yes. {context[:200]}{'...' if len(context) > 200 else ''}"
            elif any(word in context_lower for word in ["no", "false", "incorrect", "not", "never", "none"]):
                return f"Based on the provided content, the answer appears to be no. {context[:200]}{'...' if len(context) > 200 else ''}"
            else:
                return f"Based on the provided content: {context[:300]}{'...' if len(context) > 300 else ''}"
        
        # For other questions, try to extract relevant information from the context
        # Look for sentences in the context that might answer the question
        sentences = context.split('.')
        relevant_sentences = []
        
        for sentence in sentences:
            sentence_lower = sentence.lower()
            # Check if any key terms from the query are in this sentence
            for word in query_lower.split():
                if len(word) > 3 and word in sentence_lower:  # Only consider words longer than 3 chars
                    relevant_sentences.append(sentence.strip())
                    break
        
        if relevant_sentences:
            response = f"According to the book: {' '.join(relevant_sentences[:2])}"  # Take up to 2 relevant sentences
            if len(relevant_sentences) > 2:
                response += "..."
            return response
        else:
            # If no relevant sentences found, return a summary of the context
            return f"Based on the provided content: {context[:300]}{'...' if len(context) > 300 else ''}"

    def process_query(self, chat_request: ChatRequest) -> Dict[str, Any]:
        """
        Process a chat request based on the mode specified
        
        Args:
            chat_request: Chat request with query and mode
            
        Returns:
            Dictionary with response and source information
        """
        if chat_request.mode == "selected_text_only":
            if not chat_request.selected_text:
                return {
                    "response": "Selected text is required for 'selected_text_only' mode.",
                    "sources": []
                }
            return self.generate_response_selected_text_only(
                query=chat_request.query,
                selected_text=chat_request.selected_text
            )
        elif chat_request.mode == "global":
            return self.generate_response_global(query=chat_request.query)
        else:
            # Default to global mode if an invalid mode is specified
            return self.generate_response_global(query=chat_request.query)


# Global instance
rag_service = RAGService()