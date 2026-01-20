"""
Authentication Routes
Signup and signin endpoints with JWT token issuance
"""

from fastapi import APIRouter, HTTPException, status, Depends
from sqlmodel import Session
import bcrypt
from jose import jwt
from datetime import datetime, timedelta

from models import User, UserSignup, UserSignin, TokenResponse
from db import get_session
from config import BETTER_AUTH_SECRET, JWT_ALGORITHM, JWT_EXPIRATION_DAYS

router = APIRouter(prefix="/auth", tags=["Authentication"])


def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))


def create_access_token(user_id: str) -> str:
    """Create JWT access token"""
    expires_delta = timedelta(days=JWT_EXPIRATION_DAYS)
    expire = datetime.utcnow() + expires_delta

    to_encode = {
        "user_id": user_id,
        "exp": expire,
    }

    encoded_jwt = jwt.encode(to_encode, BETTER_AUTH_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt


@router.post("/signup", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def signup(
    user_data: UserSignup,
    session: Session = Depends(get_session)
):
    """
    Register a new user account

    - Validates email format (handled by Pydantic)
    - Checks for duplicate email
    - Hashes password securely
    - Creates user in database
    - Returns JWT token
    """
    # Check if user with this email already exists
    existing_user = session.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered. Please use a different email or sign in.",
        )

    # Hash the password
    password_hash = hash_password(user_data.password)

    # Create new user
    # Generate a simple user_id from email (or use UUID in production)
    user_id = user_data.email  # Using email as user_id for simplicity

    new_user = User(
        id=user_id,
        email=user_data.email,
        password_hash=password_hash,
    )

    session.add(new_user)
    session.commit()
    session.refresh(new_user)

    # Create JWT token
    access_token = create_access_token(new_user.id)

    return TokenResponse(access_token=access_token)


@router.post("/signin", response_model=TokenResponse)
async def signin(
    user_data: UserSignin,
    session: Session = Depends(get_session)
):
    """
    Sign in an existing user

    - Validates email and password
    - Returns JWT token on success
    """
    # Find user by email
    user = session.query(User).filter(User.email == user_data.email).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    # Verify password
    if not verify_password(user_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    # Create JWT token
    access_token = create_access_token(user.id)

    return TokenResponse(access_token=access_token)
