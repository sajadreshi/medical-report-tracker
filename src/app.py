import os
import glob
import re
from typing import List, Dict, Optional
from dotenv import load_dotenv
from pypdf import PdfReader
from fastapi import FastAPI, HTTPException, APIRouter
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from rag_assistant import RAGAssistant
from labreport_generator import main as generate_lab_reports

# Load environment variables
load_dotenv()

app = FastAPI(title="Medical Report Tracker")

# Create router with prefix
router = APIRouter(prefix="/medicalreport")

# Global RAG assistant instance (initialized when RAG pipeline is run)
rag_assistant: Optional[RAGAssistant] = None


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


# Pydantic models for request/response
class ChatRequest(BaseModel):
    question: str
    patient_name: Optional[str] = None


class ChatResponse(BaseModel):
    answer: str


# API Endpoints
@router.get("/", response_class=HTMLResponse)
async def read_root():
    """Serve the main UI page."""
    # Get the path to the template file
    template_path = os.path.join(os.path.dirname(__file__), "templates", "index.html")
    
    # Read the HTML file
    with open(template_path, "r", encoding="utf-8") as f:
        html_content = f.read()
    
    return HTMLResponse(content=html_content)


@router.get("/api/files")
async def list_files():
    """List unique patient names extracted from PDF files in the data directory."""
    try:
        data_dir = "data"
        pdf_files = glob.glob(os.path.join(data_dir, "*.pdf"))
        
        # Extract unique patient names from filenames
        # Pattern: LabReport_{PatientName}_Report{Number}_{Date}.pdf
        patient_names = set()
        for pdf_file in pdf_files:
            filename = os.path.basename(pdf_file)
            match = re.match(r"LabReport_(\w+)_Report\d+_\d+\.pdf", filename)
            if match:
                patient_name = match.group(1)
                patient_names.add(patient_name)
        
        # Sort patient names alphabetically
        sorted_patients = sorted(list(patient_names))
        
        return JSONResponse(content={
            "patients": sorted_patients,
            "count": len(sorted_patients),
            "total_files": len(pdf_files)
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/generate-data")
async def generate_data():
    """Generate sample lab report data."""
    try:
        # Call the lab report generator
        generate_lab_reports(num_patients=3, reports_per_patient=4, date_interval_months=1)
        return JSONResponse(content={
            "success": True,
            "message": "Sample data generated successfully",
            "reports_generated": 12
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/process-rag")
async def process_rag():
    """Process all documents in the data directory through the RAG pipeline."""
    global rag_assistant
    try:
        # Initialize the RAG assistant
        print("Initializing RAG Assistant...")
        rag_assistant = RAGAssistant()
        
        # Clear existing collection to avoid duplicates
        print("Clearing existing collection...")
        rag_assistant.vector_db.clear_collection()
        
        # Load documents
        print("Loading documents...")
        documents = load_documents()
        
        if not documents:
            return JSONResponse(content={
                "success": False,
                "message": "No documents found in data directory. Please generate sample data first.",
                "documents_processed": 0
            })
        
        # Add documents to RAG assistant
        rag_assistant.add_documents(documents)
        
        return JSONResponse(content={
            "success": True,
            "message": "RAG pipeline processed successfully",
            "documents_processed": len(documents)
        })
    except Exception as e:
        rag_assistant = None
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Chat endpoint for asking questions about the patients."""
    global rag_assistant
    
    if rag_assistant is None:
        raise HTTPException(
            status_code=400,
            detail="RAG pipeline not initialized. Please process the RAG pipeline first."
        )
    
    try:
        answer = rag_assistant.invoke(request.question, patient_name=request.patient_name)
        return ChatResponse(answer=answer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Include router in app
app.include_router(router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
