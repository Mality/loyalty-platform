
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    login = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    birth_date = Column(String, nullable=True)
    phone_number = Column(String, nullable=True)
    address = Column(String, nullable=True)
    avatar = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)

class UserRegistration(BaseModel):
    login: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8, max_length=100)
    email: EmailStr

class UserLogin(BaseModel):
    login: str
    password: str

class UserProfileUpdate(BaseModel):
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    birthDate: Optional[str] = None
    email: Optional[EmailStr] = None
    phoneNumber: Optional[str] = None
    address: Optional[str] = None
    avatar: Optional[str] = None

class UserProfile(BaseModel):
    id: str
    login: str
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    birthDate: Optional[str] = None
    email: EmailStr
    phoneNumber: Optional[str] = None
    address: Optional[str] = None
    avatar: Optional[str] = None
    createdAt: datetime
    updatedAt: datetime

class UserResponse(BaseModel):
    id: str
    login: str
    email: EmailStr
    createdAt: datetime

class AuthResponse(BaseModel):
    token: str
    expiresAt: datetime
    user: UserResponse

class Error(BaseModel):
    code: int
    message: str
    details: Optional[List[str]] = None
