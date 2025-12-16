import os
import sys
from typing import List
from pathlib import Path

# Add the project root to the path so we can import app modules
sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.utils.text_processing import split_text, preprocess_text
from app.utils.vector_store import vector_store_manager


def ingest_content_from_file(file_path: str, metadata: dict = None) -> bool:
    """
    Ingest content from a text file into the vector store
    
    Args:
        file_path: Path to the text file to ingest
        metadata: Additional metadata to store with the content
        
    Returns:
        True if successful, False otherwise
    """
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return False
    
    try:
        # Read the file content
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Preprocess the content
        processed_content = preprocess_text(content)
        
        # Split into chunks
        chunks = split_text(processed_content)
        
        # Prepare metadata for each chunk
        chunk_metadata = []
        for i, chunk in enumerate(chunks):
            chunk_meta = metadata or {}
            chunk_meta['chunk_id'] = i
            chunk_meta['source_file'] = os.path.basename(file_path)
            chunk_metadata.append(chunk_meta)
        
        print(f"Processing {len(chunks)} chunks...")
        
        # Add to vector store
        ids = vector_store_manager.add_texts(
            texts=chunks,
            metadatas=chunk_metadata
        )
        
        print(f"Successfully ingested {len(chunks)} chunks with IDs: {ids[:5]}{'...' if len(ids) > 5 else ''}")
        return True
    
    except Exception as e:
        print(f"Error ingesting content: {str(e)}")
        return False


def ingest_content_from_directory(directory_path: str, extensions: List[str] = ['.txt', '.md']) -> bool:
    """
    Ingest content from all files in a directory with specified extensions
    
    Args:
        directory_path: Path to the directory containing content files
        extensions: List of file extensions to process
        
    Returns:
        True if successful, False otherwise
    """
    if not os.path.exists(directory_path):
        print(f"Directory not found: {directory_path}")
        return False
    
    try:
        files_processed = 0
        for root, dirs, files in os.walk(directory_path):
            for file in files:
                if any(file.lower().endswith(ext) for ext in extensions):
                    file_path = os.path.join(root, file)
                    metadata = {
                        'source_directory': os.path.basename(directory_path),
                        'file_path': file_path
                    }
                    success = ingest_content_from_file(file_path, metadata)
                    if success:
                        files_processed += 1
                        print(f"Successfully processed: {file_path}")
                    else:
                        print(f"Failed to process: {file_path}")
        
        print(f"Content ingestion complete. Processed {files_processed} files.")
        return True
    
    except Exception as e:
        print(f"Error ingesting content from directory: {str(e)}")
        return False


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Ingest book content into the RAG system")
    parser.add_argument("path", help="Path to the file or directory to ingest")
    parser.add_argument("--type", choices=["file", "directory"], required=True,
                        help="Type of path provided (file or directory)")
    parser.add_argument("--extensions", nargs="+", default=[".txt", ".md"],
                        help="File extensions to process when processing a directory")
    
    args = parser.parse_args()
    
    if args.type == "file":
        success = ingest_content_from_file(args.path, metadata={"source": "manual_ingestion"})
    elif args.type == "directory":
        success = ingest_content_from_directory(args.path, args.extensions)
    else:
        print("Invalid type specified. Use 'file' or 'directory'.")
        sys.exit(1)
    
    if success:
        print("Content ingestion completed successfully.")
    else:
        print("Content ingestion failed.")
        sys.exit(1)