"""
Authentication router for login and user management.
"""
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ...db.session import get_db
from ...schemas.auth import LoginRequest, TokenResponse, UserCreate, UserResponse
from ...services.auth_service import AuthService
from ..dependencies.auth import CurrentUser, AdminUser

router = APIRouter()


@router.post("/login", response_model=TokenResponse)
async def login(
    credentials: LoginRequest,
    db: Annotated[Session, Depends(get_db)]
):
    """
    Authenticate user and return JWT tokens.
    
    - **username**: User's username
    - **password**: User's password
    """
    auth_service = AuthService(db)
    
    # Authenticate user
    user = auth_service.authenticate_user(credentials)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create tokens
    tokens = auth_service.create_tokens(user)
    return tokens


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: AdminUser
):
    """
    Register a new user (admin only).
    
    - **username**: Unique username
    - **email**: User's email address
    - **password**: Strong password (min 8 characters)
    - **role**: User role (admin, operator, viewer)
    """
    auth_service = AuthService(db)
    
    try:
        user = auth_service.create_user(user_data)
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: CurrentUser):
    """Get current user information."""
    return current_user


@router.post("/logout")
async def logout():
    """
    Logout (client-side token removal).
    The client should remove the token from storage.
    """
    return {"message": "Successfully logged out"}
