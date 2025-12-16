from typing import List
from langchain.text_splitter import RecursiveCharacterTextSplitter
from app.core.config import settings


def create_text_splitter():
    """Create a text splitter with the configured parameters"""
    return RecursiveCharacterTextSplitter(
        chunk_size=settings.CHUNK_SIZE,
        chunk_overlap=settings.CHUNK_OVERLAP,
        length_function=len,
        is_separator_regex=False,
    )


def split_text(text: str) -> List[str]:
    """
    Split text into chunks based on the configured parameters
    
    Args:
        text: The input text to split
        
    Returns:
        List of text chunks
    """
    splitter = create_text_splitter()
    chunks = splitter.split_text(text)
    
    # Filter out any chunks that are too short
    filtered_chunks = [chunk for chunk in chunks if len(chunk.strip()) > 20]
    
    return filtered_chunks


def preprocess_text(text: str) -> str:
    """
    Preprocess text before chunking
    
    Args:
        text: The input text to preprocess
        
    Returns:
        Preprocessed text
    """
    # Normalize whitespace
    text = ' '.join(text.split())
    
    # Remove extra newlines but preserve paragraph structure
    text = text.replace('\n\n', ' [PARAGRAPH_BREAK] ')
    text = text.replace('\n', ' ')
    text = text.replace('[PARAGRAPH_BREAK]', '\n\n')
    
    return text