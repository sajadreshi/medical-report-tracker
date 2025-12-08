import os
import glob
import re
from typing import List, Dict
from dotenv import load_dotenv
from pypdf import PdfReader
from rag_assistant import RAGAssistant

# Load environment variables
load_dotenv()


def load_documents() -> List[Dict]:
    """
    Load documents for demonstration.

    Returns:
        List of document dictionaries with 'content' and 'metadata' keys
    """
    results = []
    data_dir = "data"
    
    # Find all PDF files in the data directory
    pdf_files = glob.glob(os.path.join(data_dir, "*.pdf"))
    
    if not pdf_files:
        print(f"No PDF files found in {data_dir}/ directory")
        return results
    
    print(f"Found {len(pdf_files)} PDF file(s) to load...")
    
    for pdf_path in pdf_files:
        try:
            # Load PDF using pypdf directly
            reader = PdfReader(pdf_path)
            pages_text = []
            for page in reader.pages:
                pages_text.append(page.extract_text())
            
            # Combine all pages into a single document
            full_text = "\n\n".join(pages_text)
            
            # Extract metadata from filename
            filename = os.path.basename(pdf_path)
            # Parse filename: LabReport_{PatientName}_Report{Number}_{Date}.pdf
            match = re.match(r"LabReport_(\w+)_Report(\d+)_(\d+)\.pdf", filename)
            
            metadata = {
                "filename": filename,
                "filepath": pdf_path,
                "source": "lab_report"
            }
            
            if match:
                patient_name = match.group(1)
                report_number = match.group(2)
                date_str = match.group(3)
                metadata["patient_name"] = patient_name
                metadata["report_number"] = report_number
                metadata["report_date"] = date_str
            
            # Create document dictionary
            document = {
                "content": full_text,
                "metadata": metadata
            }
            
            results.append(document)
            print(f"  Loaded: {filename} ({len(reader.pages)} pages)")
            
        except Exception as e:
            print(f"  Error loading {pdf_path}: {e}")
            continue
    
    return results


def main():
    """Main function to demonstrate the RAG assistant."""
    try:
        # Initialize the RAG assistant
        print("Initializing RAG Assistant...")
        assistant = RAGAssistant()

        # Load sample documents
        print("\nLoading documents...")
        sample_docs = load_documents()
        print(f"Loaded {len(sample_docs)} sample documents")

        assistant.add_documents(sample_docs)

        done = False

        while not done:
            question = input("\nEnter a question or 'quit' to exit: ")
            if question.lower() == "quit":
                done = True
            else:
                result = assistant.invoke(question)
                print(f"\n{result}")

    except Exception as e:
        print(f"Error running RAG assistant: {e}")
        print("Make sure you have set up your .env file with at least one API key:")
        print("- OPENAI_API_KEY (OpenAI GPT models)")
        print("- GROQ_API_KEY (Groq Llama models)")
        print("- GOOGLE_API_KEY (Google Gemini models)")


if __name__ == "__main__":
    main()
