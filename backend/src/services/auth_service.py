"""
Authentication service for user management and JWT tokens.
"""
from typing import Optional
from datetime import datetime
from sqlalchemy.orm import Session

from ..db.models import User, UserRoleEnum
from ..schemas.auth import UserCreate, LoginRequest, TokenResponse
from ..core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token
)
from ..core.logging import get_logger

logger = get_logger(__name__)


class AuthService:
    """Service for authentication and user management."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def authenticate_user(self, credentials: LoginRequest) -> Optional[User]:
        """
        Authenticate a user with username and password.
        
        Args:
            credentials: Login credentials
            
        Returns:
            User if authentication successful, None otherwise
        """
        user = self.db.query(User).filter(User.username == credentials.username).first()
        
        if not user:
            logger.warning(f"Login attempt with unknown username: {credentials.username}")
            return None
        
        if not user.is_active:
            logger.warning(f"Login attempt with inactive user: {credentials.username}")
            return None
        
        if not verify_password(credentials.password, user.hashed_password):
            logger.warning(f"Invalid password for user: {credentials.username}")
            return None
        
        logger.info(f"User authenticated successfully: {credentials.username}")
        return user
    
    def create_tokens(self, user: User) -> TokenResponse:
        """
        Create access and refresh tokens for a user.
        
        Args:
            user: Authenticated user
            
        Returns:
            Token response with access and refresh tokens
        """
        access_token = create_access_token(
            data={"sub": user.username, "role": user.role.value}
        )
        refresh_token = create_refresh_token(
            data={"sub": user.username}
        )
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token
        )
    
    def create_user(self, user_data: UserCreate) -> User:
        """
        Create a new user.
        
        Args:
            user_data: User creation data
            
        Returns:
            Created user
        """
        # Check if username already exists
        existing = self.db.query(User).filter(User.username == user_data.username).first()
        if existing:
            raise ValueError(f"Username already exists: {user_data.username}")
        
        # Check if email already exists
        existing = self.db.query(User).filter(User.email == user_data.email).first()
        if existing:
            raise ValueError(f"Email already exists: {user_data.email}")
        
        # Create user
        user = User(
            username=user_data.username,
            email=user_data.email,
            full_name=user_data.full_name,
            hashed_password=get_password_hash(user_data.password),
            role=UserRoleEnum(user_data.role)
        )
        
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        
        logger.info(f"User created: {user.username} with role {user.role.value}")
        return user
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username."""
        return self.db.query(User).filter(User.username == username).first()
    
    def initialize_default_users(self):
        """Initialize default users if none exist."""
        user_count = self.db.query(User).count()
        
        if user_count == 0:
            logger.info("No users found, creating default admin user")
            
            admin_user = User(
                username="admin",
                email="admin@safelift.local",
                full_name="System Administrator",
                hashed_password=get_password_hash("admin123"),
                role=UserRoleEnum.ADMIN
            )
            
            self.db.add(admin_user)
            self.db.commit()
            
            logger.info("Default admin user created (username: admin, password: admin123)")
