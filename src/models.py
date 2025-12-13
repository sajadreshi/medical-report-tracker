"""
Database Models and Pydantic Schemas.
Defines data structures for admins, patients, and lab reports.
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime, date
import random
import string


# ============== Pydantic Request/Response Schemas ==============

# Admin Schemas
class AdminCreate(BaseModel):
    """Schema for creating a new admin."""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)


class AdminLogin(BaseModel):
    """Schema for admin login."""
    username: str
    password: str


class AdminResponse(BaseModel):
    """Schema for admin response (without password)."""
    id: int
    username: str
    email: str
    created_at: datetime
    last_login: Optional[datetime] = None


class TokenResponse(BaseModel):
    """Schema for JWT token response."""
    access_token: str
    token_type: str = "bearer"
    admin: AdminResponse


# Patient Schemas
class PatientCreate(BaseModel):
    """Schema for creating a new patient."""
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    date_of_birth: date
    sex: str = Field(..., pattern="^(Male|Female|Other)$")


class PatientUpdate(BaseModel):
    """Schema for updating patient information."""
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    date_of_birth: Optional[date] = None
    sex: Optional[str] = Field(None, pattern="^(Male|Female|Other)$")


class PatientResponse(BaseModel):
    """Schema for patient response."""
    id: int
    first_name: str
    last_name: str
    patient_id: str
    date_of_birth: date
    sex: str
    created_at: datetime
    created_by: Optional[int] = None
    report_count: Optional[int] = 0


class PatientListResponse(BaseModel):
    """Schema for paginated patient list response."""
    patients: List[PatientResponse]
    total: int
    page: int
    page_size: int


# Lab Report Schemas
class LabReportCreate(BaseModel):
    """Schema for creating a lab report record."""
    patient_id: int
    filename: str
    report_date: date
    report_number: int
    file_path: str


class LabReportResponse(BaseModel):
    """Schema for lab report response."""
    id: int
    patient_id: int
    filename: str
    report_date: date
    report_number: int
    file_path: str
    created_at: datetime


class GenerateReportsRequest(BaseModel):
    """Schema for generating lab reports request."""
    reports_count: int = Field(default=4, ge=1, le=12)
    date_interval_months: int = Field(default=1, ge=1, le=6)


# ============== Helper Functions ==============

def generate_patient_id(first_name: str, last_name: str) -> str:
    """
    Generate a unique patient ID.
    Format: First initial + Last initial + 6 random digits
    
    Args:
        first_name: Patient's first name
        last_name: Patient's last name
    
    Returns:
        Unique patient ID string
    """
    initials = f"{first_name[0].upper()}{last_name[0].upper()}"
    random_digits = ''.join(random.choices(string.digits, k=6))
    return f"{initials}{random_digits}"


def row_to_dict(row) -> dict:
    """
    Convert a sqlite3.Row object to a dictionary.
    
    Args:
        row: sqlite3.Row object
    
    Returns:
        Dictionary representation of the row
    """
    if row is None:
        return None
    return dict(row)


def rows_to_list(rows) -> List[dict]:
    """
    Convert a list of sqlite3.Row objects to a list of dictionaries.
    
    Args:
        rows: List of sqlite3.Row objects
    
    Returns:
        List of dictionary representations
    """
    return [dict(row) for row in rows]

