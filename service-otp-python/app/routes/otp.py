from fastapi import APIRouter
from app.models.otp import (
    OTPGenerateRequest,
    OTPSendRequest,
    OTPVerifyRequest,
    OTPGenerateResponse,
    OTPVerifyResponse,
    HealthResponse
)
from app.controllers import otp as otp_controller
from app.services.otp_service import otp_service
from app.middleware.rate_limit import (
    get_rate_limit_status,
    reset_rate_limit,
    clear_all_rate_limits,
    request_counters
)
import datetime

router = APIRouter(prefix="/otp", tags=["OTP Service"])

@router.post("/generate", response_model=OTPGenerateResponse)
async def generate_otp_endpoint(request: OTPGenerateRequest):
    """
    Generate OTP code and store in memory
    
    - **user_id**: Unique user identifier
    - **email**: Email address for reference
    
    Returns OTP code (for development/testing only)
    """
    return await otp_controller.generate_otp(request)

@router.post("/send", response_model=OTPGenerateResponse)
async def send_otp_endpoint(request: OTPSendRequest):
    """
    Send OTP code via email
    
    - **user_id**: User ID who will receive OTP
    - **email**: Email address to send OTP
    - **otp**: OTP code to send
    """
    return await otp_controller.send_otp(request)

@router.post("/verify", response_model=OTPVerifyResponse)
async def verify_otp_endpoint(request: OTPVerifyRequest):
    """
    Verify OTP code with rate limiting
    
    - **user_id**: User ID who generated the OTP
    - **email**: Email address for reference
    - **otp**: 6-digit OTP code to verify
    
    Rate limit: 5 attempts per minute
    """
    return await otp_controller.verify_otp(request)

# ============================================
# ADMIN / DEBUG ENDPOINTS
# ============================================

@router.get("/storage/status")
async def get_storage_status():
    """Get current in-memory storage status (Admin)"""
    return {
        "status": "success",
        "data": otp_service.get_storage_status(),
        "timestamp": datetime.datetime.now().isoformat()
    }

@router.delete("/storage/clear")
async def clear_storage():
    """Clear all OTP storage (Admin)"""
    count = otp_service.clear_storage()
    return {
        "status": "success",
        "message": f"Cleared {count} OTP records from storage",
        "timestamp": datetime.datetime.now().isoformat()
    }

@router.get("/rate-limit/{user_id}")
async def get_rate_limit(user_id: str):
    """Get rate limit status for specific user (Admin)"""
    return {
        "status": "success",
        "data": get_rate_limit_status(user_id),
        "timestamp": datetime.datetime.now().isoformat()
    }

@router.delete("/rate-limit/{user_id}")
async def reset_user_rate_limit(user_id: str):
    """Reset rate limit for specific user (Admin)"""
    result = reset_rate_limit(user_id)
    return {
        "status": "success" if result else "not_found",
        "message": f"Rate limit reset for user: {user_id}" if result else f"No rate limit record found for user: {user_id}",
        "timestamp": datetime.datetime.now().isoformat()
    }

@router.delete("/rate-limit")
async def clear_all_rate_limit():
    """Clear all rate limit records (Admin)"""
    count = clear_all_rate_limits()
    return {
        "status": "success",
        "message": f"Cleared {count} rate limit records",
        "timestamp": datetime.datetime.now().isoformat()
    }

@router.get("/stats")
async def get_stats():
    """Get overall OTP service statistics (Admin)"""
    storage_status = otp_service.get_storage_status()
    
    return {
        "status": "success",
        "data": {
            "otp_storage": {
                "total_active_users": storage_status["total_users"],
                "users": storage_status["users"]
            },
            "rate_limiting": {
                "total_tracked_users": len(request_counters),
                "users": list(request_counters.keys())
            }
        },
        "timestamp": datetime.datetime.now().isoformat()
    }