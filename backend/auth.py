import os
import jwt
import httpx
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorClient
import bcrypt

# JWT Configuration
JWT_SECRET = os.environ.get('JWT_SECRET', 'your-secret-key-change-in-production')
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION_HOURS = 24

# Google OAuth Configuration
GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET')

security = HTTPBearer()

class UserCreate(BaseModel):
    email: str
    password: str
    full_name: str

class UserLogin(BaseModel):
    email: str
    password: str

class GoogleAuthRequest(BaseModel):
    token: str

class User(BaseModel):
    id: str
    email: str
    full_name: str
    subscription_tier: str = "free"  # free, mid, pro
    credits_remaining: int = 0
    subscription_expires: Optional[datetime] = None
    created_at: datetime
    is_active: bool = True

class AuthService:
    def __init__(self, db):
        self.db = db
        
    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    
    def create_access_token(self, user_id: str, email: str) -> str:
        """Create JWT access token"""
        payload = {
            'user_id': user_id,
            'email': email,
            'exp': datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS),
            'iat': datetime.utcnow()
        }
        return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify JWT token and return payload"""
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )
        except jwt.JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
    
    async def register_user(self, user_data: UserCreate) -> User:
        """Register a new user"""
        # Check if user already exists
        existing_user = await self.db.users.find_one({"email": user_data.email})
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create new user
        hashed_password = self.hash_password(user_data.password)
        user_doc = {
            "id": str(uuid.uuid4()),
            "email": user_data.email,
            "password_hash": hashed_password,
            "full_name": user_data.full_name,
            "subscription_tier": "free",
            "credits_remaining": 5,  # Free tier gets 5 credits
            "subscription_expires": None,
            "created_at": datetime.utcnow(),
            "is_active": True
        }
        
        await self.db.users.insert_one(user_doc)
        
        # Return user without password
        user_doc.pop('password_hash')
        return User(**user_doc)
    
    async def authenticate_user(self, login_data: UserLogin) -> tuple[User, str]:
        """Authenticate user and return user + token"""
        user_doc = await self.db.users.find_one({"email": login_data.email})
        if not user_doc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        if not self.verify_password(login_data.password, user_doc['password_hash']):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        if not user_doc.get('is_active', True):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Account is disabled"
            )
        
        # Create access token
        token = self.create_access_token(user_doc['id'], user_doc['email'])
        
        # Return user without password
        user_doc.pop('password_hash')
        user = User(**user_doc)
        
        return user, token
    
    async def google_auth(self, auth_request: GoogleAuthRequest) -> tuple[User, str]:
        """Authenticate with Google OAuth"""
        try:
            # Verify Google token
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"https://www.googleapis.com/oauth2/v1/tokeninfo?access_token={auth_request.token}"
                )
                
                if response.status_code != 200:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Invalid Google token"
                    )
                
                google_data = response.json()
                email = google_data.get('email')
                name = google_data.get('name', email.split('@')[0])
                
                if not email:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Could not get email from Google"
                    )
                
                # Check if user exists
                user_doc = await self.db.users.find_one({"email": email})
                
                if not user_doc:
                    # Create new user from Google data
                    user_doc = {
                        "id": str(uuid.uuid4()),
                        "email": email,
                        "full_name": name,
                        "subscription_tier": "free",
                        "credits_remaining": 5,
                        "subscription_expires": None,
                        "created_at": datetime.utcnow(),
                        "is_active": True,
                        "google_id": google_data.get('user_id')
                    }
                    await self.db.users.insert_one(user_doc)
                
                # Create access token
                token = self.create_access_token(user_doc['id'], user_doc['email'])
                
                # Return user
                user_doc.pop('password_hash', None)
                user = User(**user_doc)
                
                return user, token
                
        except httpx.RequestError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Could not verify Google token"
            )
    
    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        user_doc = await self.db.users.find_one({"id": user_id})
        if user_doc:
            user_doc.pop('password_hash', None)
            return User(**user_doc)
        return None

# Dependency to get current user
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db = Depends(get_database)
) -> User:
    """Get current authenticated user"""
    auth_service = AuthService(db)
    
    try:
        payload = auth_service.verify_token(credentials.credentials)
        user_id = payload.get('user_id')
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )
        
        user = await auth_service.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        return user
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )

# Optional authentication (for public endpoints that can benefit from user context)
async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
    db = Depends(get_database)
) -> Optional[User]:
    """Get current user if authenticated, otherwise None"""
    if not credentials:
        return None
    
    try:
        return await get_current_user(credentials, db)
    except:
        return None

import uuid
from models import get_database