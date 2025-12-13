"""
Authentication Module.
Handles password hashing, JWT token generation/validation, and authentication dependencies.
"""

import os
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv

from database import get_db
from models import row_to_dict

# Load environment variables
load_dotenv()

# Security configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production-12345")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))  # 24 hours default

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# HTTP Bearer token security
security = HTTPBearer()


# ============== Password Utilities ==============

def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt.
    
    Args:
        password: Plain text password
    
    Returns:
        Hashed password string
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash.
    
    Args:
        plain_password: Plain text password to verify
        hashed_password: Hashed password to compare against
    
    Returns:
        True if password matches, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


# ============== JWT Token Utilities ==============

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.
    
    Args:
        data: Data to encode in the token
        expires_delta: Optional custom expiration time
    
    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> Optional[dict]:
    """
    Decode and validate a JWT token.
    
    Args:
        token: JWT token string
    
    Returns:
        Decoded token payload or None if invalid
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


# ============== Admin Database Operations ==============

def get_admin_by_username(username: str) -> Optional[dict]:
    """
    Get an admin by username.
    
    Args:
        username: Admin username
    
    Returns:
        Admin dictionary or None if not found
    """
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM admins WHERE username = ?",
            (username,)
        )
        row = cursor.fetchone()
        return row_to_dict(row)


def get_admin_by_email(email: str) -> Optional[dict]:
    """
    Get an admin by email.
    
    Args:
        email: Admin email
    
    Returns:
        Admin dictionary or None if not found
    """
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM admins WHERE email = ?",
            (email,)
        )
        row = cursor.fetchone()
        return row_to_dict(row)


def get_admin_by_id(admin_id: int) -> Optional[dict]:
    """
    Get an admin by ID.
    
    Args:
        admin_id: Admin ID
    
    Returns:
        Admin dictionary or None if not found
    """
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM admins WHERE id = ?",
            (admin_id,)
        )
        row = cursor.fetchone()
        return row_to_dict(row)


def create_admin(username: str, email: str, password: str) -> dict:
    """
    Create a new admin user.
    
    Args:
        username: Admin username
        email: Admin email
        password: Plain text password (will be hashed)
    
    Returns:
        Created admin dictionary
    
    Raises:
        HTTPException: If username or email already exists
    """
    # Check if username exists
    if get_admin_by_username(username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Check if email exists
    if get_admin_by_email(email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Hash password and create admin
    password_hash = hash_password(password)
    
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO admins (username, email, password_hash)
            VALUES (?, ?, ?)
            """,
            (username, email, password_hash)
        )
        admin_id = cursor.lastrowid
    
    return get_admin_by_id(admin_id)


def authenticate_admin(username: str, password: str) -> Optional[dict]:
    """
    Authenticate an admin by username and password.
    
    Args:
        username: Admin username
        password: Plain text password
    
    Returns:
        Admin dictionary if authenticated, None otherwise
    """
    admin = get_admin_by_username(username)
    
    if not admin:
        return None
    
    if not verify_password(password, admin["password_hash"]):
        return None
    
    # Update last login
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE admins SET last_login = ? WHERE id = ?",
            (datetime.utcnow(), admin["id"])
        )
    
    return admin


# ============== Authentication Dependency ==============

async def get_current_admin(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """
    FastAPI dependency to get the current authenticated admin.
    
    Args:
        credentials: HTTP Bearer credentials
    
    Returns:
        Current admin dictionary
    
    Raises:
        HTTPException: If token is invalid or admin not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    token = credentials.credentials
    payload = decode_token(token)
    
    if payload is None:
        raise credentials_exception
    
    admin_id = payload.get("sub")
    if admin_id is None:
        raise credentials_exception
    
    admin = get_admin_by_id(int(admin_id))
    if admin is None:
        raise credentials_exception
    
    return admin


# Optional authentication - returns None if not authenticated
async def get_current_admin_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))
) -> Optional[dict]:
    """
    FastAPI dependency to optionally get the current authenticated admin.
    Returns None if not authenticated instead of raising an exception.
    
    Args:
        credentials: Optional HTTP Bearer credentials
    
    Returns:
        Current admin dictionary or None
    """
    if credentials is None:
        return None
    
    token = credentials.credentials
    payload = decode_token(token)
    
    if payload is None:
        return None
    
    admin_id = payload.get("sub")
    if admin_id is None:
        return None
    
    return get_admin_by_id(int(admin_id))

