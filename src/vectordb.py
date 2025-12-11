import os
import chromadb
from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer
from langchain_text_splitters import RecursiveCharacterTextSplitter


class VectorDB:
    """
    A simple vector database wrapper using ChromaDB with HuggingFace embeddings.
    """

    def __init__(self, collection_name: str = None, embedding_model: str = None):
        """
        Initialize the vector database.

        Args:
            collection_name: Name of the ChromaDB collection
            embedding_model: HuggingFace model name for embeddings
        """
        self.collection_name = collection_name or os.getenv(
            "CHROMA_COLLECTION_NAME", "rag_lab_reports"
        )
        self.embedding_model_name = embedding_model or os.getenv(
            "EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2"
        )

        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(path="./chroma_db")

        # Load embedding model
        print(f"Loading embedding model: {self.embedding_model_name}")
        self.embedding_model = SentenceTransformer(self.embedding_model_name)

        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"description": "RAG document collection"},
        )

        print(f"Vector database initialized with collection: {self.collection_name}")

    def clear_collection(self) -> None:
        """
        Clear all documents from the collection.
        Deletes the existing collection and recreates it to ensure a fresh start.
        """
        try:
            # Delete the existing collection if it exists
            self.client.delete_collection(name=self.collection_name)
            print(f"Deleted existing collection: {self.collection_name}")
        except Exception as e:
            # Collection might not exist yet, which is fine
            print(f"Collection {self.collection_name} does not exist yet or could not be deleted: {e}")
        
        # Recreate the collection
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"description": "RAG document collection"},
        )
        print(f"Collection {self.collection_name} cleared and ready for new documents")

    def chunk_text(self, text: str, chunk_size: int = 500) -> List[str]:
        """
        Simple text chunking by splitting on spaces and grouping into chunks.

        Args:
            text: Input text to chunk
            chunk_size: Approximate number of characters per chunk

        Returns:
            List of text chunks
        """
        # Use LangChain's RecursiveCharacterTextSplitter for better chunking
        # This preserves sentence boundaries and handles context better
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_size // 10,  # 10% overlap for context preservation
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        
        chunks = text_splitter.split_text(text)
        return chunks

    def add_documents(self, documents: List) -> None:
        """
        Add documents to the vector database.

        Args:
            documents: List of documents with 'content' and 'metadata' keys
        """
        print(f"Processing {len(documents)} documents...")
        
        all_chunks = []
        all_metadatas = []
        all_ids = []
        
        for doc_idx, document in enumerate(documents):
            # Extract content and metadata
            content = document.get('content', '')
            metadata = document.get('metadata', {})
            
            if not content:
                print(f"Warning: Document {doc_idx} has no content, skipping...")
                continue
            
            # Chunk the document
            chunks = self.chunk_text(content)
            
            # Create IDs and metadata for each chunk
            for chunk_idx, chunk in enumerate(chunks):
                chunk_id = f"doc_{doc_idx}_chunk_{chunk_idx}"
                all_ids.append(chunk_id)
                all_chunks.append(chunk)
                
                # Add chunk index to metadata
                chunk_metadata = metadata.copy()
                chunk_metadata['chunk_index'] = chunk_idx
                chunk_metadata['total_chunks'] = len(chunks)
                all_metadatas.append(chunk_metadata)
            
            print(f"  Document {doc_idx + 1}/{len(documents)}: Created {len(chunks)} chunks")
        
        if not all_chunks:
            print("No chunks to add to vector database")
            return
        
        # Create embeddings for all chunks
        print(f"Creating embeddings for {len(all_chunks)} chunks...")
        embeddings = self.embedding_model.encode(all_chunks, show_progress_bar=True)
        
        # Convert embeddings to list format for ChromaDB
        embeddings_list = embeddings.tolist()
        
        # Add to ChromaDB collection
        print(f"Storing {len(all_chunks)} chunks in vector database...")
        self.collection.add(
            ids=all_ids,
            embeddings=embeddings_list,
            documents=all_chunks,
            metadatas=all_metadatas
        )
        
        print(f"Successfully added {len(all_chunks)} chunks from {len(documents)} documents to vector database")

    def search(self, query: str, n_results: int = 5) -> Dict[str, Any]:
        """
        Search for similar documents in the vector database.

        Args:
            query: Search query
            n_results: Number of results to return

        Returns:
            Dictionary containing search results with keys: 'documents', 'metadatas', 'distances', 'ids'
        """
        # Create query embedding
        query_embedding = self.embedding_model.encode([query])
        query_embedding_list = query_embedding.tolist()
        
        # Query ChromaDB
        results = self.collection.query(
            query_embeddings=query_embedding_list,
            n_results=n_results
        )
        
        # Handle empty results
        if not results['ids'] or not results['ids'][0]:
            return {
                "documents": [],
                "metadatas": [],
                "distances": [],
                "ids": [],
            }
        
        # ChromaDB returns results as lists of lists, so we need to extract the first element
        return {
            "documents": results['documents'][0] if results.get('documents') else [],
            "metadatas": results['metadatas'][0] if results.get('metadatas') else [],
            "distances": results['distances'][0] if results.get('distances') else [],
            "ids": results['ids'][0] if results.get('ids') else [],
        }
