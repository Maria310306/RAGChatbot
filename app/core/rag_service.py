from typing import List, Dict, Any
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from app.utils.vector_store import vector_store_manager
from app.core.config import settings
from app.schemas.chat import ChatRequest


class RAGService:
    def __init__(self):
        self.llm = ChatOpenAI(
            model=settings.GPT_MODEL,
            temperature=0.1,  # Lower temperature for more consistent responses
            max_tokens=1000
        )
        
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
        
        # Create chain and generate response
        qa_chain = RetrievalQA.from_llm(
            llm=self.llm,
            retriever=None,  # We're handling retrieval manually
            prompt=self.global_rag_prompt
        )
        
        # Format the prompt with context and question
        formatted_prompt = self.global_rag_prompt.format(
            context=context,
            question=query
        )
        
        # Manually call the LLM with the formatted prompt
        response = self.llm.invoke(formatted_prompt)
        
        # Extract sources
        sources = [doc.metadata for doc in docs] if docs else []
        
        return {
            "response": response.content,
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
        # Create chain and generate response using only selected text
        formatted_prompt = self.selected_text_prompt.format(
            selected_text=selected_text,
            question=query
        )
        
        # Call the LLM with the formatted prompt
        response = self.llm.invoke(formatted_prompt)
        
        return {
            "response": response.content,
            "sources": [{"source": "selected_text", "content": selected_text}]
        }
    
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