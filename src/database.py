"""
SQLite Database Connection and Initialization Module.
Handles database setup, connection management, and table creation.
"""

import sqlite3
import os
from datetime import datetime
from contextlib import contextmanager
from typing import Optional

# Database file path
DATABASE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "medical_reports.db")


def get_connection() -> sqlite3.Connection:
    """
    Get a database connection with row factory enabled.
    
    Returns:
        sqlite3.Connection: Database connection object
    """
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row  # Enable dict-like access to rows
    return conn


@contextmanager
def get_db():
    """
    Context manager for database connections.
    Automatically handles connection closing.
    
    Yields:
        sqlite3.Connection: Database connection object
    """
    conn = get_connection()
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def init_database():
    """
    Initialize the database and create all tables.
    This function is idempotent - safe to call multiple times.
    """
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Create admins table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS admins (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP
            )
        """)
        
        # Create patients table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS patients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                patient_id TEXT UNIQUE NOT NULL,
                date_of_birth DATE NOT NULL,
                sex TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_by INTEGER,
                FOREIGN KEY (created_by) REFERENCES admins(id)
            )
        """)
        
        # Create lab_reports table for tracking generated reports
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS lab_reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER NOT NULL,
                filename TEXT NOT NULL,
                report_date DATE NOT NULL,
                report_number INTEGER NOT NULL,
                file_path TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (patient_id) REFERENCES patients(id)
            )
        """)
        
        # Create indexes for better query performance
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_patients_patient_id ON patients(patient_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_patients_last_name ON patients(last_name)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_lab_reports_patient_id ON lab_reports(patient_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_admins_username ON admins(username)
        """)
        
        print("Database initialized successfully.")


def drop_all_tables():
    """
    Drop all tables in the database.
    WARNING: This will delete all data!
    """
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("DROP TABLE IF EXISTS lab_reports")
        cursor.execute("DROP TABLE IF EXISTS patients")
        cursor.execute("DROP TABLE IF EXISTS admins")
        print("All tables dropped.")


def reset_database():
    """
    Reset the database by dropping all tables and recreating them.
    WARNING: This will delete all data!
    """
    drop_all_tables()
    init_database()
    print("Database reset complete.")


# Initialize database on module import
if __name__ == "__main__":
    init_database()

