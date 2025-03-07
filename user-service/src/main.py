from fastapi import FastAPI, Depends, HTTPException, status, Header
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta
import os
from jose import jwt
from passlib.context import CryptContext
import uvicorn
from model import Base, User, UserRegistration, UserLogin, UserResponse, UserProfile, UserProfileUpdate, Error, AuthResponse

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app = FastAPI(title="User Service API", description="API for user management, authentication and authorization")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = os.getenv("JWT_SECRET", "your-secret-key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt, expire

def get_user_by_login(db: Session, login: str):
    return db.query(User).filter(User.login == login).first()

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def get_user_by_id(db: Session, user_id: str):
    return db.query(User).filter(User.id == user_id).first()


async def get_current_user(authorization: str = Header(None), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    if not authorization or not authorization.startswith("Bearer "):
        raise credentials_exception
    
    token = authorization.replace("Bearer ", "")
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except jwt.JWTError:
        raise credentials_exception
        
    user = get_user_by_id(db, user_id)
    if user is None:
        raise credentials_exception
    
    return user

@app.post("/api/v1/auth/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED, tags=["auth"])
async def register_user(user_data: UserRegistration, db: Session = Depends(get_db)):
    if get_user_by_login(db, user_data.login):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=Error(code=409, message="User with this login already exists").dict()
        )
    
    if get_user_by_email(db, user_data.email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=Error(code=409, message="User with this email already exists").dict()
        )
    
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        login=user_data.login,
        email=user_data.email,
        password_hash=hashed_password
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return UserResponse(
        id=new_user.id,
        login=new_user.login,
        email=new_user.email,
        createdAt=new_user.created_at
    )

@app.post("/api/v1/auth/login", response_model=AuthResponse, tags=["auth"])
async def login_user(user_data: UserLogin, db: Session = Depends(get_db)):
    user = get_user_by_login(db, user_data.login)
    
    if not user or not verify_password(user_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=Error(code=401, message="Invalid credentials").dict()
        )
    
    token, expires_at = create_access_token(
        data={"sub": user.id},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    return AuthResponse(
        token=token,
        expiresAt=expires_at,
        user=UserResponse(
            id=user.id,
            login=user.login,
            email=user.email,
            createdAt=user.created_at
        )
    )

@app.get("/api/v1/users/profile", response_model=UserProfile, tags=["users"])
async def get_user_profile(current_user: User = Depends(get_current_user)):
    return UserProfile(
        id=current_user.id,
        login=current_user.login,
        firstName=current_user.first_name,
        lastName=current_user.last_name,
        birthDate=current_user.birth_date,
        email=current_user.email,
        phoneNumber=current_user.phone_number,
        address=current_user.address,
        avatar=current_user.avatar,
        createdAt=current_user.created_at,
        updatedAt=current_user.updated_at
    )

@app.put("/api/v1/users/profile", response_model=UserProfile, tags=["users"])
async def update_user_profile(
    profile_update: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if profile_update.firstName is not None:
        current_user.first_name = profile_update.firstName
    
    if profile_update.lastName is not None:
        current_user.last_name = profile_update.lastName
    
    if profile_update.birthDate is not None:
        current_user.birth_date = profile_update.birthDate
    
    if profile_update.email is not None:
        existing_user = get_user_by_email(db, profile_update.email)
        if existing_user and existing_user.id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=Error(code=400, message="Email already in use").dict()
            )
        current_user.email = profile_update.email
    
    if profile_update.phoneNumber is not None:
        current_user.phone_number = profile_update.phoneNumber
    
    if profile_update.address is not None:
        current_user.address = profile_update.address
    
    if profile_update.avatar is not None:
        current_user.avatar = profile_update.avatar
    
    current_user.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(current_user)
    
    return UserProfile(
        id=current_user.id,
        login=current_user.login,
        firstName=current_user.first_name,
        lastName=current_user.last_name,
        birthDate=current_user.birth_date,
        email=current_user.email,
        phoneNumber=current_user.phone_number,
        address=current_user.address,
        avatar=current_user.avatar,
        createdAt=current_user.created_at,
        updatedAt=current_user.updated_at
    )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
