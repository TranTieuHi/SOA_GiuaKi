from fastapi import APIRouter, Depends, HTTPException
from app.controllers.auth import login_user, register_user
from app.models.user import LoginRequest, RegisterRequest

router = APIRouter()

@router.post("/login")  # ✅ /api/auth/login
def login(credentials: LoginRequest):  # <--- XÓA ASYNC
    """
    Login user and return JWT token
    """
    return login_user(credentials)
  
@router.post("/register")  # ✅ /api/auth/register
def register(user_data: RegisterRequest):
    """
    Register new user
    
    POST /api/auth/register
    {
      "username": "johndoe",
      "email": "john@example.com",
      "password": "password123",
      "full_name": "John Doe"
    }
    """
    return register_user(user_data)