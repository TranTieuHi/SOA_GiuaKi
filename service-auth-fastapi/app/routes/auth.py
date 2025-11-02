from fastapi import APIRouter, Depends
from app.controllers.auth import login_user, register_user, get_user_profile, force_refresh_user_data
from app.models.user import LoginRequest, RegisterRequest
from app.middleware.auth_middleware import get_current_user

router = APIRouter(prefix="/auth")

@router.post("/login")
async def login(credentials: LoginRequest):
    """User login"""
    return login_user(credentials)

@router.post("/register")
async def register(user_data: RegisterRequest):
    """User registration"""
    return register_user(user_data)

@router.get("/profile")
async def profile(current_user: dict = Depends(get_current_user)):
    """Get current user profile - PROTECTED ROUTE"""
    return get_user_profile(current_user["user_id"])

# ✅ Add force refresh endpoint
@router.post("/profile/refresh")
async def force_refresh_profile(current_user: dict = Depends(get_current_user)):
    """Force refresh user profile with guaranteed fresh data"""
    return force_refresh_user_data(current_user["user_id"])