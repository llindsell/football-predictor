from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from google.oauth2 import id_token
from google.auth.transport import requests
from sqlmodel import Session, select
from .database import get_session
from .models import User
from .config import settings
import jwt
from datetime import datetime, timedelta

router = APIRouter()

class LoginRequest(BaseModel):
    credential: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: User

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

@router.post("/login", response_model=LoginResponse)
def login(request: LoginRequest, session: Session = Depends(get_session)):
    try:
        # Verify the Google token
        id_info = id_token.verify_oauth2_token(
            request.credential, 
            requests.Request(), 
            audience=settings.GOOGLE_CLIENT_ID,
            clock_skew_in_seconds=10
        )
        
        email = id_info.get("email")
        name = id_info.get("name")
        picture = id_info.get("picture")
        
        if not email:
            raise HTTPException(status_code=400, detail="Invalid token: Email not found")

        # Check if user exists, create if not
        user = session.exec(select(User).where(User.email == email)).first()
        if not user:
            user = User(email=email, name=name, profile_picture=picture)
            session.add(user)
            session.commit()
            session.refresh(user)
        
        # Create JWT token
        access_token = create_access_token(data={"sub": str(user.id)})
        
        return LoginResponse(
            access_token=access_token,
            token_type="bearer",
            user=user
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid token: {str(e)}")

from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def get_current_user(token: str = Depends(oauth2_scheme), session: Session = Depends(get_session)):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Could not validate credentials")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")
    
    user = session.get(User, int(user_id))
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user

@router.get("/me", response_model=LoginResponse)
def read_users_me(current_user: User = Depends(get_current_user)):
    access_token = create_access_token(data={"sub": str(current_user.id)})
    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        user=current_user
    )
