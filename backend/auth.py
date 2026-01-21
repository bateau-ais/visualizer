"""
NOVA Visualizer - Authentication
=================================

JWT-based authentication system with password hashing and token management.
"""

import os
from datetime import datetime, timedelta
from typing import Optional
import logging

from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from models.user import User, TokenData, UserRole

logger = logging.getLogger(__name__)

# Password hashing context
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

# JWT settings
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "INSECURE_DEFAULT_KEY_CHANGE_ME")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRATION_MINUTES", "60"))

# Security scheme
security = HTTPBearer()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.
    
    Args:
        data: Payload to encode
        expires_delta: Token expiration time (default: ACCESS_TOKEN_EXPIRE_MINUTES)
    
    Returns:
        Encoded JWT token
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt


def decode_access_token(token: str) -> TokenData:
    """
    Decode and validate a JWT token.
    
    Args:
        token: JWT token string
    
    Returns:
        TokenData with username and role
    
    Raises:
        HTTPException: If token is invalid or expired
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        role: str = payload.get("role")
        
        if username is None or role is None:
            raise HTTPException(status_code=401, detail="Invalid token payload")
        
        return TokenData(username=username, role=role)
    
    except JWTError as e:
        logger.warning(f"JWT decode error: {e}")
        raise HTTPException(
            status_code=401,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> TokenData:
    """
    Dependency to verify JWT token from Authorization header.
    
    Usage:
        @router.get("/protected")
        async def protected_route(token_data: TokenData = Depends(verify_token)):
            ...
    """
    token = credentials.credentials
    return decode_access_token(token)


def require_role(required_role: UserRole):
    """
    Dependency factory to check user role.
    
    Usage:
        @router.post("/admin-only")
        async def admin_route(token_data: TokenData = Depends(require_role(UserRole.ADMIN))):
            ...
    """
    async def role_checker(token_data: TokenData = Depends(verify_token)) -> TokenData:
        user_role = UserRole(token_data.role)
        
        # Role hierarchy: ADMIN > OPERATOR > VIEWER
        role_hierarchy = {
            UserRole.VIEWER: 0,
            UserRole.OPERATOR: 1,
            UserRole.ADMIN: 2
        }
        
        if role_hierarchy[user_role] < role_hierarchy[required_role]:
            raise HTTPException(
                status_code=403,
                detail=f"Insufficient permissions. Required: {required_role.value}"
            )
        
        return token_data
    
    return role_checker


# In-memory user store (REPLACE WITH DATABASE IN PRODUCTION!)
USERS_DB: dict[str, User] = {}


def init_default_users():
    """Initialize default users for demo."""
    global USERS_DB
    
    # Create default admin user
    if "admin" not in USERS_DB:
        USERS_DB["admin"] = User(
            username="admin",
            hashed_password=get_password_hash("admin123"),  # ⚠️ CHANGE IN PRODUCTION!
            role=UserRole.ADMIN,
            created_at=datetime.utcnow(),
            is_active=True
        )
        logger.info("✅ Default admin user created (username: admin, password: admin123)")
    
    # Create default operator user
    if "operator" not in USERS_DB:
        USERS_DB["operator"] = User(
            username="operator",
            hashed_password=get_password_hash("operator123"),
            role=UserRole.OPERATOR,
            created_at=datetime.utcnow(),
            is_active=True
        )
        logger.info("✅ Default operator user created (username: operator, password: operator123)")
    
    # Create default viewer user
    if "viewer" not in USERS_DB:
        USERS_DB["viewer"] = User(
            username="viewer",
            hashed_password=get_password_hash("viewer123"),
            role=UserRole.VIEWER,
            created_at=datetime.utcnow(),
            is_active=True
        )
        logger.info("✅ Default viewer user created (username: viewer, password: viewer123)")


def get_user(username: str) -> Optional[User]:
    """Get user by username."""
    return USERS_DB.get(username)


def authenticate_user(username: str, password: str) -> Optional[User]:
    """
    Authenticate a user with username and password.
    
    Returns:
        User object if authentication successful, None otherwise
    """
    user = get_user(username)
    
    if not user:
        return None
    
    if not user.is_active:
        return None
    
    if not verify_password(password, user.hashed_password):
        return None
    
    return user


def create_user(username: str, password: str, role: UserRole = UserRole.VIEWER) -> User:
    """
    Create a new user.
    
    Raises:
        ValueError: If username already exists
    """
    if username in USERS_DB:
        raise ValueError(f"User '{username}' already exists")
    
    user = User(
        username=username,
        hashed_password=get_password_hash(password),
        role=role,
        created_at=datetime.utcnow(),
        is_active=True
    )
    
    USERS_DB[username] = user
    logger.info(f"✅ User created: {username} (role: {role.value})")
    
    return user
