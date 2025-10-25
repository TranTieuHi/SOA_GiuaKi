from fastapi import APIRouter
from app.models.user import LoginRequest, RegisterRequest, LoginResponse
from app.controllers import auth

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/login", response_model=LoginResponse)
def login_endpoint(credentials: LoginRequest):
    """API đăng nhập"""
    return auth.login_user(credentials)

@router.post("/register", status_code=201)
def register_endpoint(data: RegisterRequest):
    """API đăng ký"""
    return auth.register_user(data)