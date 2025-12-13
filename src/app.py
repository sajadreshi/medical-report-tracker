"""
FastAPI Application for Medical Report Tracker.
Includes authentication, admin functionality, patient management, and RAG pipeline.
"""

import os
import glob
import re
from datetime import datetime, date
from typing import List, Dict, Optional
from dotenv import load_dotenv
from pypdf import PdfReader
from fastapi import FastAPI, HTTPException, APIRouter, Depends, Query
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel

# Import local modules
from database import init_database, get_db
from models import (
    AdminCreate, AdminLogin, AdminResponse, TokenResponse,
    PatientCreate, PatientUpdate, PatientResponse, PatientListResponse,
    GenerateReportsRequest
)
from auth import (
    create_access_token, authenticate_admin, create_admin,
    get_current_admin, get_admin_by_id
)
from patient_service import (
    create_patient, get_patient_by_id, get_patient_by_patient_id,
    update_patient, delete_patient, list_patients, search_patients,
    create_lab_report, get_patient_lab_reports, delete_patient_lab_reports,
    get_all_patients_with_reports
)
from rag_assistant import RAGAssistant
import labreport_generator

# Load environment variables
load_dotenv()

# Initialize database
init_database()

# Create FastAPI app
app = FastAPI(title="Medical Report Tracker")

# Create router with prefix
router = APIRouter(prefix="/medicalreport")

# Global RAG assistant instance
rag_assistant: Optional[RAGAssistant] = None


# ============== Request/Response Models ==============

class ChatRequest(BaseModel):
    message: str
    patient_name: Optional[str] = None


class ProcessRagResponse(BaseModel):
    success: bool
    message: str
    documents_processed: int


# ============== Helper Functions ==============

def load_documents(patient_filter: Optional[str] = None) -> List[Dict]:
    """
    Load documents from PDF files in the data directory.
    
    Args:
        patient_filter: Optional patient name to filter documents
    
    Returns:
        List of document dictionaries with 'content' and 'metadata' keys
    """
    results = []
    data_dir = "data"
    
    pdf_files = glob.glob(os.path.join(data_dir, "*.pdf"))
    
    if not pdf_files:
        print(f"No PDF files found in {data_dir}/ directory")
        return results
    
    print(f"Found {len(pdf_files)} PDF file(s) to load...")
    
    for pdf_path in pdf_files:
        try:
            reader = PdfReader(pdf_path)
            pages_text = []
            for page in reader.pages:
                pages_text.append(page.extract_text())
            
            full_text = "\n\n".join(pages_text)
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
                
                # Apply patient filter if specified
                if patient_filter and patient_name.upper() != patient_filter.upper():
                    continue
            
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


def get_unique_patients_from_files() -> List[str]:
    """
    Get unique patient names from PDF files in the data directory.
    
    Returns:
        Sorted list of unique patient names
    """
    data_dir = "data"
    pdf_files = glob.glob(os.path.join(data_dir, "*.pdf"))
    
    patients = set()
    for pdf_path in pdf_files:
        filename = os.path.basename(pdf_path)
        match = re.match(r"LabReport_(\w+)_Report\d+_\d+\.pdf", filename)
        if match:
            patients.add(match.group(1))
    
    return sorted(list(patients))


# ============== HTML Page Routes ==============

@router.get("/", response_class=HTMLResponse)
async def get_home_page():
    """Serve the home page."""
    template_path = os.path.join(os.path.dirname(__file__), "templates", "home.html")
    try:
        with open(template_path, "r") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Home template not found")


@router.get("/dashboard", response_class=HTMLResponse)
async def get_dashboard():
    """Serve the admin dashboard page."""
    template_path = os.path.join(os.path.dirname(__file__), "templates", "index.html")
    try:
        with open(template_path, "r") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Dashboard template not found")


@router.get("/login", response_class=HTMLResponse)
async def get_login_page():
    """Serve the login page."""
    template_path = os.path.join(os.path.dirname(__file__), "templates", "login.html")
    try:
        with open(template_path, "r") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Login template not found")


# ============== Authentication Routes ==============

@router.post("/api/auth/register", response_model=AdminResponse)
async def register_admin(admin_data: AdminCreate):
    """Register a new admin user."""
    admin = create_admin(admin_data.username, admin_data.email, admin_data.password)
    return AdminResponse(
        id=admin["id"],
        username=admin["username"],
        email=admin["email"],
        created_at=admin["created_at"],
        last_login=admin.get("last_login")
    )


@router.post("/api/auth/login", response_model=TokenResponse)
async def login_admin(login_data: AdminLogin):
    """Authenticate admin and return JWT token."""
    admin = authenticate_admin(login_data.username, login_data.password)
    
    if not admin:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password"
        )
    
    access_token = create_access_token(data={"sub": str(admin["id"])})
    
    return TokenResponse(
        access_token=access_token,
        admin=AdminResponse(
            id=admin["id"],
            username=admin["username"],
            email=admin["email"],
            created_at=admin["created_at"],
            last_login=admin.get("last_login")
        )
    )


@router.get("/api/auth/me", response_model=AdminResponse)
async def get_current_admin_info(current_admin: dict = Depends(get_current_admin)):
    """Get current authenticated admin information."""
    return AdminResponse(
        id=current_admin["id"],
        username=current_admin["username"],
        email=current_admin["email"],
        created_at=current_admin["created_at"],
        last_login=current_admin.get("last_login")
    )


# ============== Patient Management Routes ==============

@router.post("/api/admin/patients", response_model=PatientResponse)
async def create_new_patient(
    patient_data: PatientCreate,
    current_admin: dict = Depends(get_current_admin)
):
    """Create a new patient."""
    patient = create_patient(patient_data, created_by=current_admin["id"])
    return PatientResponse(
        id=patient["id"],
        first_name=patient["first_name"],
        last_name=patient["last_name"],
        patient_id=patient["patient_id"],
        date_of_birth=patient["date_of_birth"],
        sex=patient["sex"],
        created_at=patient["created_at"],
        created_by=patient.get("created_by"),
        report_count=patient.get("report_count", 0)
    )


@router.get("/api/admin/patients", response_model=PatientListResponse)
async def list_all_patients(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    current_admin: dict = Depends(get_current_admin)
):
    """List all patients with pagination and optional search."""
    patients, total = list_patients(page=page, page_size=page_size, search=search)
    
    return PatientListResponse(
        patients=[
            PatientResponse(
                id=p["id"],
                first_name=p["first_name"],
                last_name=p["last_name"],
                patient_id=p["patient_id"],
                date_of_birth=p["date_of_birth"],
                sex=p["sex"],
                created_at=p["created_at"],
                created_by=p.get("created_by"),
                report_count=p.get("report_count", 0)
            ) for p in patients
        ],
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/api/admin/patients/search")
async def search_patients_endpoint(
    q: str = Query(..., min_length=1),
    limit: int = Query(10, ge=1, le=50),
    current_admin: dict = Depends(get_current_admin)
):
    """Search patients by name or patient ID."""
    patients = search_patients(q, limit=limit)
    return {
        "patients": [
            PatientResponse(
                id=p["id"],
                first_name=p["first_name"],
                last_name=p["last_name"],
                patient_id=p["patient_id"],
                date_of_birth=p["date_of_birth"],
                sex=p["sex"],
                created_at=p["created_at"],
                created_by=p.get("created_by"),
                report_count=p.get("report_count", 0)
            ) for p in patients
        ]
    }


@router.get("/api/admin/patients/{patient_db_id}", response_model=PatientResponse)
async def get_patient(
    patient_db_id: int,
    current_admin: dict = Depends(get_current_admin)
):
    """Get a patient by database ID."""
    patient = get_patient_by_id(patient_db_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    return PatientResponse(
        id=patient["id"],
        first_name=patient["first_name"],
        last_name=patient["last_name"],
        patient_id=patient["patient_id"],
        date_of_birth=patient["date_of_birth"],
        sex=patient["sex"],
        created_at=patient["created_at"],
        created_by=patient.get("created_by"),
        report_count=patient.get("report_count", 0)
    )


@router.put("/api/admin/patients/{patient_db_id}", response_model=PatientResponse)
async def update_patient_endpoint(
    patient_db_id: int,
    patient_data: PatientUpdate,
    current_admin: dict = Depends(get_current_admin)
):
    """Update a patient's information."""
    patient = update_patient(patient_db_id, patient_data)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    return PatientResponse(
        id=patient["id"],
        first_name=patient["first_name"],
        last_name=patient["last_name"],
        patient_id=patient["patient_id"],
        date_of_birth=patient["date_of_birth"],
        sex=patient["sex"],
        created_at=patient["created_at"],
        created_by=patient.get("created_by"),
        report_count=patient.get("report_count", 0)
    )


@router.delete("/api/admin/patients/{patient_db_id}")
async def delete_patient_endpoint(
    patient_db_id: int,
    current_admin: dict = Depends(get_current_admin)
):
    """Delete a patient, their lab report files, and their vector database data."""
    global rag_assistant
    
    # Get patient info before deleting
    patient = get_patient_by_id(patient_db_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    patient_last_name = patient["last_name"].upper()
    deleted_files = 0
    deleted_vectors = 0
    
    # 1. Delete PDF files for this patient
    data_dir = "data"
    pdf_pattern = os.path.join(data_dir, f"LabReport_{patient_last_name}_*.pdf")
    existing_pdfs = glob.glob(pdf_pattern)
    for pdf_file in existing_pdfs:
        try:
            os.remove(pdf_file)
            deleted_files += 1
        except OSError as e:
            print(f"Warning: Could not delete {pdf_file}: {e}")
    
    # 2. Delete vector database data for this patient
    try:
        if rag_assistant is None:
            rag_assistant = RAGAssistant()
        deleted_vectors = rag_assistant.vector_db.delete_patient_documents(patient_last_name)
    except Exception as e:
        print(f"Warning: Could not delete vector data for {patient_last_name}: {e}")
    
    # 3. Delete patient from database (includes lab_reports records)
    if not delete_patient(patient_db_id):
        raise HTTPException(status_code=404, detail="Patient not found")
    
    return {
        "success": True, 
        "message": f"Patient {patient['last_name']}, {patient['first_name']} deleted successfully",
        "files_deleted": deleted_files,
        "vectors_deleted": deleted_vectors
    }


# ============== Lab Report Generation Routes ==============

@router.post("/api/admin/patients/{patient_db_id}/generate-reports")
async def generate_patient_reports(
    patient_db_id: int,
    request: GenerateReportsRequest,
    current_admin: dict = Depends(get_current_admin)
):
    """Generate lab reports for a specific patient."""
    patient = get_patient_by_id(patient_db_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    try:
        # Delete existing reports for this patient
        deleted_count = delete_patient_lab_reports(patient_db_id)
        
        # Generate new reports using the patient's information
        generated_files = labreport_generator.generate_for_patient(
            patient_info={
                "first_name": patient["first_name"],
                "last_name": patient["last_name"],
                "patient_id": patient["patient_id"],
                "date_of_birth": patient["date_of_birth"],
                "sex": patient["sex"]
            },
            reports_count=request.reports_count,
            date_interval_months=request.date_interval_months
        )
        
        # Record reports in database
        for report_info in generated_files:
            create_lab_report(
                patient_db_id=patient_db_id,
                filename=report_info["filename"],
                report_date=report_info["report_date"],
                report_number=report_info["report_number"],
                file_path=report_info["file_path"]
            )
        
        return {
            "success": True,
            "message": f"Generated {len(generated_files)} lab reports for {patient['last_name']}, {patient['first_name']}",
            "reports_generated": len(generated_files),
            "reports_deleted": deleted_count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating reports: {str(e)}")


@router.get("/api/admin/patients/{patient_db_id}/reports")
async def get_patient_reports(
    patient_db_id: int,
    current_admin: dict = Depends(get_current_admin)
):
    """Get all lab reports for a patient."""
    patient = get_patient_by_id(patient_db_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    reports = get_patient_lab_reports(patient_db_id)
    return {"patient_id": patient_db_id, "reports": reports}


# ============== RAG Pipeline Routes ==============

@router.post("/api/admin/rag/process", response_model=ProcessRagResponse)
async def process_rag_pipeline(current_admin: dict = Depends(get_current_admin)):
    """Process RAG pipeline for all documents in data directory (appends to existing data)."""
    global rag_assistant
    
    try:
        print("Initializing RAG Assistant...")
        rag_assistant = RAGAssistant()
        
        # Load documents (appending to existing data)
        print("Loading documents...")
        documents = load_documents()
        
        if not documents:
            return ProcessRagResponse(
                success=False,
                message="No documents found in data directory",
                documents_processed=0
            )
        
        # Add documents to vector database
        rag_assistant.add_documents(documents)
        
        return ProcessRagResponse(
            success=True,
            message=f"Successfully processed {len(documents)} documents",
            documents_processed=len(documents)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing RAG pipeline: {str(e)}")


@router.post("/api/admin/patients/{patient_db_id}/process-rag", response_model=ProcessRagResponse)
async def process_rag_pipeline_for_patient(
    patient_db_id: int,
    current_admin: dict = Depends(get_current_admin)
):
    """Process RAG pipeline for a specific patient's documents only (replaces old data for this patient)."""
    global rag_assistant
    
    patient = get_patient_by_id(patient_db_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    patient_last_name = patient["last_name"].upper()
    
    try:
        print(f"Initializing RAG Assistant for patient: {patient_last_name}...")
        rag_assistant = RAGAssistant()
        
        # Delete old documents for this patient before adding new ones
        deleted_count = rag_assistant.vector_db.delete_patient_documents(patient_last_name)
        if deleted_count > 0:
            print(f"Cleared {deleted_count} old documents for patient {patient_last_name}")
        
        # Load documents filtered by patient
        print(f"Loading documents for patient: {patient_last_name}...")
        documents = load_documents(patient_filter=patient_last_name)
        
        if not documents:
            return ProcessRagResponse(
                success=False,
                message=f"No documents found for patient {patient['last_name']}, {patient['first_name']}",
                documents_processed=0
            )
        
        # Add documents to vector database
        rag_assistant.add_documents(documents)
        
        return ProcessRagResponse(
            success=True,
            message=f"Successfully processed {len(documents)} documents for {patient['last_name']}, {patient['first_name']}",
            documents_processed=len(documents)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing RAG pipeline: {str(e)}")


@router.post("/api/chat")
async def chat_with_assistant(
    request: ChatRequest,
    current_admin: dict = Depends(get_current_admin)
):
    """Chat with the RAG assistant about patient lab reports."""
    global rag_assistant
    
    if rag_assistant is None:
        raise HTTPException(
            status_code=400,
            detail="RAG pipeline not initialized. Please process documents first."
        )
    
    try:
        response = rag_assistant.invoke(
            input=request.message,
            patient_name=request.patient_name
        )
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing chat: {str(e)}")


# ============== Legacy/Public Routes (for backward compatibility) ==============

@router.get("/api/files")
async def list_files():
    """List unique patient names from files in data directory."""
    patients = get_unique_patients_from_files()
    pdf_files = glob.glob(os.path.join("data", "*.pdf"))
    
    return {
        "patients": patients,
        "total_files": len(pdf_files)
    }


@router.post("/api/generate-data")
async def generate_sample_data(current_admin: dict = Depends(get_current_admin)):
    """Generate sample lab reports (admin only)."""
    try:
        labreport_generator.main(num_patients=3, reports_per_patient=4, date_interval_months=1)
        return {
            "success": True,
            "message": "Generated 12 sample lab reports (3 patients × 4 reports each)"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating data: {str(e)}")


@router.post("/api/process-rag")
async def process_rag_legacy(current_admin: dict = Depends(get_current_admin)):
    """Legacy endpoint for processing RAG pipeline."""
    return await process_rag_pipeline(current_admin)


# ============== Public Patients Route (for chat) ==============

@router.get("/api/patients-with-reports")
async def get_patients_with_reports(current_admin: dict = Depends(get_current_admin)):
    """Get all patients who have lab reports (from database or files)."""
    # First try to get from database
    db_patients = get_all_patients_with_reports()
    
    if db_patients:
        return {
            "patients": [
                {
                    "id": p["id"],
                    "name": f"{p['last_name']}, {p['first_name']}",
                    "patient_id": p["patient_id"],
                    "report_count": p.get("report_count", 0)
                } for p in db_patients
            ],
            "source": "database"
        }
    
    # Fall back to file-based patient list
    file_patients = get_unique_patients_from_files()
    return {
        "patients": [{"name": p, "patient_id": None, "report_count": 0} for p in file_patients],
        "source": "files"
    }


# Include router in app
app.include_router(router)


# ============== Main Entry Point ==============

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
