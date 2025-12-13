# Methodology

The Medical Report Tracker employs a **Retrieval-Augmented Generation (RAG)** methodology to enable intelligent querying of patient lab results. The approach combines semantic search capabilities with generative AI to provide accurate, context-aware responses.

## Document Processing Pipeline

The system follows a structured pipeline for processing lab reports: **Extraction → Chunking → Embedding → Storage → Retrieval → Generation**. PDF documents are first loaded and text content is extracted using PyPDF, preserving the structured format of lab reports. Metadata such as patient name, report number, and date are automatically extracted from filenames using regular expression pattern matching.

## Text Chunking Strategy

Documents are segmented using LangChain's RecursiveCharacterTextSplitter with a chunk size of 500 characters and 10% overlap between chunks. This approach ensures that related information spans across chunk boundaries, maintaining context continuity while optimizing for retrieval efficiency. The chunking strategy prioritizes sentence boundaries and paragraph breaks to preserve semantic coherence.

## Embedding and Vector Storage

Each document chunk is converted into a dense vector representation using HuggingFace's `sentence-transformers/all-MiniLM-L6-v2` model, which generates 384-dimensional embeddings capturing semantic meaning. These embeddings are stored in ChromaDB, a persistent vector database that enables efficient similarity search. The vector database maintains associations between embeddings, original text chunks, and metadata, allowing for both semantic retrieval and metadata-based filtering.

## Query Processing Methodology

When processing user queries, the system employs a two-stage retrieval approach: **semantic search followed by optional patient filtering**. The query is first converted to an embedding vector, and cosine similarity is used to retrieve the most relevant document chunks from the vector database. If a patient is selected, results are post-filtered to include only chunks associated with that patient's metadata, ensuring query responses are scoped to the relevant patient context.

## Response Generation

The retrieved context chunks are combined with the user's question and formatted according to a predefined prompt template. This prompt instructs the LLM to answer based solely on the provided context, ensuring responses are grounded in the actual lab report data. The system supports multiple LLM providers (OpenAI, Groq, Google Gemini) through a unified interface, allowing flexibility in model selection based on performance requirements and cost considerations.

## Data Generation for Testing

For demonstration and testing purposes, the methodology includes a synthetic data generation component using the Faker library to create realistic patient demographics and the ReportLab library to generate standardized PDF lab reports. This approach enables comprehensive testing of the RAG pipeline without requiring access to real patient data, while maintaining the structural and formatting characteristics of authentic medical documents.

