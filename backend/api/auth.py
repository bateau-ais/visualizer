"""
NOVA Visualizer - Authentication API
=====================================

Endpoints for user authentication and authorization.
"""

from fastapi import APIRouter, HTTPException, Depends
from datetime import timedelta
import logging

from models.user import UserLogin, UserCreate, Token, User, UserRole
from auth import (
    authenticate_user,
    create_access_token,
    create_user,
    verify_token,
    require_role,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    USERS_DB,
    TokenData
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/auth", tags=["authentication"])


@router.post("/login", response_model=Token)
async def login(credentials: UserLogin):
    """
    Authenticate user and return JWT token.
    
    **Usage:**
    ```bash
    curl -X POST http://localhost:8000/auth/login \
      -H "Content-Type: application/json" \
      -d '{"username": "admin", "password": "admin123"}'
    ```
    """
    user = authenticate_user(credentials.username, credentials.password)
    
    if not user:
        logger.warning(f"Failed login attempt for username: {credentials.username}")
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Update last login
    user.last_login = user.created_at.__class__.utcnow()
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role.value},
        expires_delta=access_token_expires
    )
    
    logger.info(f"✅ User logged in: {user.username} (role: {user.role.value})")
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        user={
            "username": user.username,
            "role": user.role.value,
            "last_login": user.last_login.isoformat() if user.last_login else None
        }
    )


@router.get("/me")
async def get_current_user(token_data: TokenData = Depends(verify_token)):
    """
    Get current authenticated user info.
    
    **Requires:** Valid JWT token in Authorization header
    """
    user = USERS_DB.get(token_data.username)
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "username": user.username,
        "role": user.role.value,
        "created_at": user.created_at.isoformat(),
        "last_login": user.last_login.isoformat() if user.last_login else None
    }


@router.post("/register", response_model=dict)
async def register_user(
    user_data: UserCreate,
    token_data: TokenData = Depends(require_role(UserRole.ADMIN))
):
    """
    Register a new user.
    
    **Requires:** ADMIN role
    """
    try:
        user = create_user(
            username=user_data.username,
            password=user_data.password,
            role=user_data.role
        )
        
        return {
            "message": f"User '{user.username}' created successfully",
            "username": user.username,
            "role": user.role.value
        }
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/users")
async def list_users(token_data: TokenData = Depends(require_role(UserRole.ADMIN))):
    """
    List all users.
    
    **Requires:** ADMIN role
    """
    return {
        "users": [
            {
                "username": user.username,
                "role": user.role.value,
                "created_at": user.created_at.isoformat(),
                "last_login": user.last_login.isoformat() if user.last_login else None,
                "is_active": user.is_active
            }
            for user in USERS_DB.values()
        ]
    }


@router.post("/logout")
async def logout(token_data: TokenData = Depends(verify_token)):
    """
    Logout (client-side token deletion).
    
    Note: JWT tokens cannot be invalidated server-side without a token blacklist.
    Clients should delete the token immediately.
    """
    logger.info(f"User logged out: {token_data.username}")
    
    return {"message": "Logged out successfully. Please delete your token."}
