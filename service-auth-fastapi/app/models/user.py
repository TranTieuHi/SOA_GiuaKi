from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class LoginRequest(BaseModel):
    username: str  # Can be username or email
    password: str

class RegisterRequest(BaseModel):
    username: str
    email_address: EmailStr
    password: str
    full_name: str
    phone_number: Optional[str] = None

class User(BaseModel):
    user_id: str
    username: str
    email_address: str
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    available_balance: float

class LoginResponse(BaseModel):
    success: bool
    statusCode: int
    message: str
    token: str
    user: User

class RegisterResponse(BaseModel):
    success: bool
    statusCode: int
    message: str
    user: dict