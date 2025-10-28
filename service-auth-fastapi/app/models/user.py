from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class User(BaseModel):
    """Model cho User (response)"""
    user_id: str
    username: str
    email_address: EmailStr
    full_name: str
    phone_number: Optional[str] = None
    available_balance: float = 0.0

class RegisterRequest(BaseModel):
    """Model cho Register request"""
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)
    email_address: EmailStr = Field(...) # Tên đúng là email_address
    full_name: str = Field(..., min_length=1, max_length=100)
    phone_number: Optional[str] = Field(None, max_length=20)

class LoginRequest(BaseModel):
    """Model cho Login request"""
    username: str = Field(..., description="Username")
    password: str = Field(..., description="Password")

    class Config:
        json_schema_extra = {
            "example": {
                "username": "johndoe",
                "password": "password123"
            }
        }

class LoginResponse(BaseModel):
    """Model cho Login response"""
    success: bool
    statusCode: int
    message: str
    token: str
    user: User

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "statusCode": 200,
                "message": "Login successful",
                "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "user": {
                    "user_id": "USR1737618000000",
                    "username": "johndoe",
                    "email_address": "johndoe@example.com",
                    "full_name": "John Doe",
                    "phone_number": "1234567890",
                    "available_balance": 100000000.0
                }
            }
        }