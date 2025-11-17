"""
Document processing and ingestion into ChromaDB
Handles loading, chunking, and embedding of hospital documents
"""

import os
import time
from typing import List, Tuple
from pathlib import Path

from langchain_community.document_loaders import TextLoader, DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, AzureOpenAIEmbeddings
from langchain_google_genai import GoogleGenerativeAIEmbeddings  # NEW: Gemini support
from langchain_community.vectorstores import Chroma
from langchain.schema import Document

from backend.config import settings



class DocumentProcessor:
    """
    Handles document loading, chunking, and ingestion into ChromaDB
    
    Features:
    - Loads documents from directory
    - Splits into overlapping chunks
    - Creates embeddings (Gemini / OpenAI / Azure)
    - Stores in ChromaDB with metadata
    """
    
    def __init__(self):
        """Initialize document processor with configuration"""
        self.documents_path = settings.DOCUMENTS_PATH
        self.chunk_size = settings.CHUNK_SIZE
        self.chunk_overlap = settings.CHUNK_OVERLAP
        self.persist_directory = settings.CHROMA_PERSIST_DIRECTORY
        self.collection_name = settings.CHROMA_COLLECTION_NAME
        
        # Initialize embeddings
        self.embeddings = self._initialize_embeddings()
        
        # Ensure persist directory exists
        Path(self.persist_directory).mkdir(parents=True, exist_ok=True)
        print(f"✓ Vector database directory: {self.persist_directory}")
    
    def _initialize_embeddings(self):
        """
        Initialize embedding model based on configuration
        
        Returns:
            Embeddings instance (Gemini / Azure / OpenAI)
        """
        embedding_config = settings.get_embedding_config()
        provider = embedding_config["provider"]
        
        if provider == "azure":
            print("✓ Using Azure OpenAI embeddings...")
            return AzureOpenAIEmbeddings(
                azure_endpoint=embedding_config["azure_endpoint"],
                api_key=embedding_config["api_key"],
                api_version=embedding_config["api_version"],
                azure_deployment=embedding_config["deployment_name"],
                model=embedding_config["model"]
            )
        
        elif provider == "openai":
            print("✓ Using OpenAI embeddings...")
            return OpenAIEmbeddings(
                api_key=embedding_config["api_key"],
                model=embedding_config["model"]
            )
        
        elif provider == "gemini":
            print("✓ Using Google Gemini embeddings (models/gemini-embedding-001)...")
            return GoogleGenerativeAIEmbeddings(
                model=embedding_config["model"],  # e.g., "models/gemini-embedding-001"
                google_api_key=embedding_config["api_key"],
                dimensions=768,  # Balanced dim (reduce storage/speed up search; full=3072)
                # task_type auto-set by LangChain: RETRIEVAL_DOCUMENT for docs, RETRIEVAL_QUERY for queries
            )
        
        else:
            raise ValueError(f"❌ Unsupported embedding provider: {provider}")
    
    def load_documents(self) -> List[Document]:
        """
        Load all text documents from the documents directory
        
        Returns:
            List of Document objects
            
        Raises:
            FileNotFoundError: If documents directory doesn't exist
            ValueError: If no documents found in directory
        """
        print(f"\n📂 Loading documents from: {self.documents_path}")
        
        if not os.path.exists(self.documents_path):
            raise FileNotFoundError(
                f"❌ Documents directory not found: {self.documents_path}"
            )
        
        # Load all .txt files from directory
        loader = DirectoryLoader(
            self.documents_path,
            glob="**/*.txt",
            loader_cls=TextLoader,
            loader_kwargs={"encoding": "utf-8"}
        )
        
        try:
            documents = loader.load()
        except Exception as e:
            raise ValueError(f"❌ Error loading documents: {str(e)}")
        
        print(f"✓ Loaded {len(documents)} documents")
        
        if len(documents) == 0:
            raise ValueError(
                f"❌ No .txt files found in {self.documents_path}. "
                "Please add documents to this directory."
            )
        
        return documents
    
    def split_documents(self, documents: List[Document]) -> List[Document]:
        """
        Split documents into overlapping chunks for embedding
        
        Args:
            documents: List of Document objects
        
        Returns:
            List of chunked Document objects with metadata
        """
        print(f"\n✂️ Splitting documents into chunks...")
        print(f"   Chunk size: {self.chunk_size} tokens")
        print(f"   Overlap: {self.chunk_overlap} tokens")
        
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""],
            is_separator_regex=False
        )
        
        chunks = text_splitter.split_documents(documents)
        print(f"✓ Created {len(chunks)} chunks from {len(documents)} documents")
        
        # Add chunk index to metadata
        for i, chunk in enumerate(chunks):
            chunk.metadata["chunk_index"] = i
            chunk.metadata["chunk_size"] = len(chunk.page_content)
        
        return chunks
    
    def ingest_documents(self, force_reindex: bool = False) -> Tuple[int, int, float]:
        """
        Main ingestion pipeline: load, chunk, and store documents
        
        Args:
            force_reindex: If True, clear existing collection and re-index
        
        Returns:
            Tuple of (documents_processed, chunks_created, time_taken)
            
        Raises:
            Various exceptions during processing
        """
        start_time = time.time()
        
        print(f"\n{'='*60}")
        print(f"Document Ingestion Pipeline Started")
        print(f"{'='*60}")
        
        if not force_reindex:
            try:
                existing_db = Chroma(
                    collection_name=self.collection_name,
                    embedding_function=self.embeddings,
                    persist_directory=self.persist_directory
                )
                existing_count = existing_db._collection.count()
                
                if existing_count > 0:
                    print(f"⚠️  Collection already exists with {existing_count} chunks")
                    print(f"    To re-index, set force_reindex=True")
                    return (0, existing_count, 0.0)
            except Exception:
                pass
        
        documents = self.load_documents()
        chunks = self.split_documents(documents)
        
        print(f"\n🗄️  Creating vector store...")
        print(f"    Collection: {self.collection_name}")
        print(f"    Directory: {self.persist_directory}")
        
        try:
            vectorstore = Chroma.from_documents(
                documents=chunks,
                embedding=self.embeddings,
                collection_name=self.collection_name,
                persist_directory=self.persist_directory
            )
            print(f"✓ Vector store created successfully")
        except Exception as e:
            raise RuntimeError(f"❌ Failed to create vector store: {str(e)}")
        
        elapsed_time = time.time() - start_time
        
        print(f"\n{'='*60}")
        print(f"✅ Ingestion Completed Successfully!")
        print(f"   Documents: {len(documents)}")
        print(f"   Chunks: {len(chunks)}")
        print(f"   Time: {elapsed_time:.2f} seconds")
        print(f"{'='*60}\n")
        
        return (len(documents), len(chunks), elapsed_time)
    
    def get_vectorstore(self) -> Chroma:
        """
        Get existing vector store instance for querying
        
        Returns:
            ChromaDB vector store instance
        """
        return Chroma(
            collection_name=self.collection_name,
            embedding_function=self.embeddings,
            persist_directory=self.persist_directory
        )
    
    def get_document_count(self) -> int:
        """
        Get count of document chunks in vector store
        
        Returns:
            Number of document chunks (0 if collection doesn't exist)
        """
        try:
            vectorstore = self.get_vectorstore()
            count = vectorstore._collection.count()
            return count
        except Exception:
            return 0


# Create global instance
document_processor = DocumentProcessor()