"""RAG Assistant for querying medical lab reports."""

import os
from typing import List, Optional
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv

from vectordb import VectorDB
from llms import initialize_llm
from utils import PromptBuilder

# Load environment variables
load_dotenv()


class RAGAssistant:
    """
    A simple RAG-based AI assistant using ChromaDB and multiple LLM providers.
    Supports OpenAI, Groq, and Google Gemini APIs.
    """

    def __init__(self, model: Optional[str] = None, prompt_name: str = "rag_assistant"):
        """
        Initialize the RAG assistant.
        
        Args:
            model: Optional model name. If None, uses initialize_llm() to detect from env vars.
            prompt_name: Name of the prompt template to load from YAML config.
        """
        # Initialize LLM
        self.llm = initialize_llm(model=model)

        # Initialize vector database
        self.vector_db = VectorDB()

        # Load prompt template from YAML
        prompt_builder = PromptBuilder()
        self.prompt_template = prompt_builder.build_prompt(prompt_name=prompt_name)

        # Create the chain
        self.chain = self.prompt_template | self.llm | StrOutputParser()

        print("RAG Assistant initialized successfully")

    def add_documents(self, documents: List) -> None:
        """
        Add documents to the knowledge base.

        Args:
            documents: List of documents
        """
        self.vector_db.add_documents(documents)

    def invoke(self, input: str, n_results: Optional[int] = None, patient_name: Optional[str] = None) -> str:
        """
        Query the RAG assistant.

        Args:
            input: User's input/question
            n_results: Number of relevant chunks to retrieve. If None, uses RAG_N_RESULTS from .env or default 50.
            patient_name: Optional patient name to filter context and add to question.

        Returns:
            String answer from the LLM based on retrieved context
        """
        # Get n_results from parameter, environment variable, or use default
        if n_results is None:
            n_results = int(os.getenv("RAG_N_RESULTS", "50"))
        
        # Search for relevant context chunks
        search_results = self.vector_db.search(input, n_results=n_results)
        
        # Filter by patient name if provided
        if patient_name:
            filtered_docs = []
            filtered_metadatas = []
            filtered_ids = []
            filtered_distances = []
            
            for i, doc in enumerate(search_results['documents']):
                metadata = search_results['metadatas'][i] if search_results.get('metadatas') else {}
                if metadata.get('patient_name', '').upper() == patient_name.upper():
                    filtered_docs.append(doc)
                    filtered_metadatas.append(metadata)
                    if search_results.get('ids'):
                        filtered_ids.append(search_results['ids'][i])
                    if search_results.get('distances'):
                        filtered_distances.append(search_results['distances'][i])
            
            if not filtered_docs:
                return f"I couldn't find any information about patient {patient_name} in the lab reports."
            
            search_results = {
                'documents': filtered_docs,
                'metadatas': filtered_metadatas,
                'ids': filtered_ids if filtered_ids else [],
                'distances': filtered_distances if filtered_distances else []
            }
        
        # Combine retrieved chunks into context string
        if not search_results['documents']:
            return "I couldn't find any relevant information in the lab reports to answer your question."
        
        context_parts = []
        for i, doc in enumerate(search_results['documents']):
            metadata = search_results['metadatas'][i] if search_results.get('metadatas') else {}
            doc_patient_name = metadata.get('patient_name', 'Unknown')
            report_number = metadata.get('report_number', 'Unknown')
            
            context_parts.append(f"[Report from {doc_patient_name}, Report #{report_number}]\n{doc}")
        
        context = "\n\n---\n\n".join(context_parts)
        
        # Add patient context to question if provided
        question = input
        if patient_name:
            question = f"Ask questions about {patient_name}. {input}"
        
        # Generate response using the chain
        try:
            response = self.chain.invoke({
                "context": context,
                "question": question
            })
            return response
        except Exception as e:
            return f"Error generating response: {e}"

