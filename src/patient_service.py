"""
Patient Service Module.
Handles patient CRUD operations and lab report management.
"""

from typing import Optional, List, Tuple
from datetime import date, datetime
from database import get_db
from models import (
    PatientCreate,
    PatientUpdate,
    PatientResponse,
    generate_patient_id,
    row_to_dict,
    rows_to_list
)


# ============== Patient CRUD Operations ==============

def create_patient(patient_data: PatientCreate, created_by: Optional[int] = None) -> dict:
    """
    Create a new patient.
    
    Args:
        patient_data: Patient creation data
        created_by: Admin ID who created the patient
    
    Returns:
        Created patient dictionary
    """
    # Generate unique patient ID
    patient_id = generate_patient_id(patient_data.first_name, patient_data.last_name)
    
    # Ensure patient_id is unique
    while get_patient_by_patient_id(patient_id):
        patient_id = generate_patient_id(patient_data.first_name, patient_data.last_name)
    
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO patients (first_name, last_name, patient_id, date_of_birth, sex, created_by)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                patient_data.first_name,
                patient_data.last_name,
                patient_id,
                patient_data.date_of_birth.isoformat(),
                patient_data.sex,
                created_by
            )
        )
        new_id = cursor.lastrowid
    
    return get_patient_by_id(new_id)


def get_patient_by_id(patient_id: int) -> Optional[dict]:
    """
    Get a patient by database ID.
    
    Args:
        patient_id: Patient database ID
    
    Returns:
        Patient dictionary or None if not found
    """
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT p.*, 
                   (SELECT COUNT(*) FROM lab_reports lr WHERE lr.patient_id = p.id) as report_count
            FROM patients p
            WHERE p.id = ?
            """,
            (patient_id,)
        )
        row = cursor.fetchone()
        return row_to_dict(row)


def get_patient_by_patient_id(patient_id: str) -> Optional[dict]:
    """
    Get a patient by their patient ID (e.g., 'JD123456').
    
    Args:
        patient_id: Patient ID string
    
    Returns:
        Patient dictionary or None if not found
    """
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT p.*, 
                   (SELECT COUNT(*) FROM lab_reports lr WHERE lr.patient_id = p.id) as report_count
            FROM patients p
            WHERE p.patient_id = ?
            """,
            (patient_id,)
        )
        row = cursor.fetchone()
        return row_to_dict(row)


def update_patient(patient_db_id: int, patient_data: PatientUpdate) -> Optional[dict]:
    """
    Update a patient's information.
    
    Args:
        patient_db_id: Patient database ID
        patient_data: Patient update data
    
    Returns:
        Updated patient dictionary or None if not found
    """
    # Build dynamic update query
    updates = []
    values = []
    
    if patient_data.first_name is not None:
        updates.append("first_name = ?")
        values.append(patient_data.first_name)
    
    if patient_data.last_name is not None:
        updates.append("last_name = ?")
        values.append(patient_data.last_name)
    
    if patient_data.date_of_birth is not None:
        updates.append("date_of_birth = ?")
        values.append(patient_data.date_of_birth.isoformat())
    
    if patient_data.sex is not None:
        updates.append("sex = ?")
        values.append(patient_data.sex)
    
    if not updates:
        return get_patient_by_id(patient_db_id)
    
    values.append(patient_db_id)
    
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            f"UPDATE patients SET {', '.join(updates)} WHERE id = ?",
            tuple(values)
        )
    
    return get_patient_by_id(patient_db_id)


def delete_patient(patient_db_id: int) -> bool:
    """
    Delete a patient and their lab reports.
    
    Args:
        patient_db_id: Patient database ID
    
    Returns:
        True if deleted, False if not found
    """
    patient = get_patient_by_id(patient_db_id)
    if not patient:
        return False
    
    with get_db() as conn:
        cursor = conn.cursor()
        # Delete associated lab reports first
        cursor.execute("DELETE FROM lab_reports WHERE patient_id = ?", (patient_db_id,))
        # Delete patient
        cursor.execute("DELETE FROM patients WHERE id = ?", (patient_db_id,))
    
    return True


def list_patients(
    page: int = 1,
    page_size: int = 20,
    search: Optional[str] = None
) -> Tuple[List[dict], int]:
    """
    List patients with pagination and optional search.
    
    Args:
        page: Page number (1-indexed)
        page_size: Number of results per page
        search: Optional search term for name or patient ID
    
    Returns:
        Tuple of (list of patients, total count)
    """
    offset = (page - 1) * page_size
    
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Build query with optional search
        if search:
            search_pattern = f"%{search}%"
            cursor.execute(
                """
                SELECT COUNT(*) FROM patients
                WHERE first_name LIKE ? OR last_name LIKE ? OR patient_id LIKE ?
                """,
                (search_pattern, search_pattern, search_pattern)
            )
            total = cursor.fetchone()[0]
            
            cursor.execute(
                """
                SELECT p.*, 
                       (SELECT COUNT(*) FROM lab_reports lr WHERE lr.patient_id = p.id) as report_count
                FROM patients p
                WHERE first_name LIKE ? OR last_name LIKE ? OR patient_id LIKE ?
                ORDER BY p.created_at DESC
                LIMIT ? OFFSET ?
                """,
                (search_pattern, search_pattern, search_pattern, page_size, offset)
            )
        else:
            cursor.execute("SELECT COUNT(*) FROM patients")
            total = cursor.fetchone()[0]
            
            cursor.execute(
                """
                SELECT p.*, 
                       (SELECT COUNT(*) FROM lab_reports lr WHERE lr.patient_id = p.id) as report_count
                FROM patients p
                ORDER BY p.created_at DESC
                LIMIT ? OFFSET ?
                """,
                (page_size, offset)
            )
        
        patients = rows_to_list(cursor.fetchall())
    
    return patients, total


def search_patients(query: str, limit: int = 10) -> List[dict]:
    """
    Search patients by name or patient ID.
    
    Args:
        query: Search query
        limit: Maximum number of results
    
    Returns:
        List of matching patients
    """
    search_pattern = f"%{query}%"
    
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT p.*, 
                   (SELECT COUNT(*) FROM lab_reports lr WHERE lr.patient_id = p.id) as report_count
            FROM patients p
            WHERE first_name LIKE ? OR last_name LIKE ? OR patient_id LIKE ?
            ORDER BY last_name, first_name
            LIMIT ?
            """,
            (search_pattern, search_pattern, search_pattern, limit)
        )
        return rows_to_list(cursor.fetchall())


# ============== Lab Report Operations ==============

def create_lab_report(
    patient_db_id: int,
    filename: str,
    report_date: date,
    report_number: int,
    file_path: str
) -> dict:
    """
    Create a lab report record.
    
    Args:
        patient_db_id: Patient database ID
        filename: Report filename
        report_date: Date of the report
        report_number: Report number for the patient
        file_path: Full file path to the PDF
    
    Returns:
        Created lab report dictionary
    """
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO lab_reports (patient_id, filename, report_date, report_number, file_path)
            VALUES (?, ?, ?, ?, ?)
            """,
            (patient_db_id, filename, report_date.isoformat(), report_number, file_path)
        )
        report_id = cursor.lastrowid
        
        cursor.execute("SELECT * FROM lab_reports WHERE id = ?", (report_id,))
        return row_to_dict(cursor.fetchone())


def get_patient_lab_reports(patient_db_id: int) -> List[dict]:
    """
    Get all lab reports for a patient.
    
    Args:
        patient_db_id: Patient database ID
    
    Returns:
        List of lab report dictionaries
    """
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT * FROM lab_reports
            WHERE patient_id = ?
            ORDER BY report_date DESC, report_number DESC
            """,
            (patient_db_id,)
        )
        return rows_to_list(cursor.fetchall())


def delete_patient_lab_reports(patient_db_id: int) -> int:
    """
    Delete all lab reports for a patient.
    
    Args:
        patient_db_id: Patient database ID
    
    Returns:
        Number of reports deleted
    """
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT COUNT(*) FROM lab_reports WHERE patient_id = ?",
            (patient_db_id,)
        )
        count = cursor.fetchone()[0]
        
        cursor.execute("DELETE FROM lab_reports WHERE patient_id = ?", (patient_db_id,))
    
    return count


def get_all_patients_with_reports() -> List[dict]:
    """
    Get all patients who have at least one lab report.
    
    Returns:
        List of patient dictionaries with report counts
    """
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT p.*, 
                   (SELECT COUNT(*) FROM lab_reports lr WHERE lr.patient_id = p.id) as report_count
            FROM patients p
            WHERE EXISTS (SELECT 1 FROM lab_reports lr WHERE lr.patient_id = p.id)
            ORDER BY p.last_name, p.first_name
            """
        )
        return rows_to_list(cursor.fetchall())

