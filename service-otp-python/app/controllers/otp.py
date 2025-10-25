from fastapi import HTTPException
from app.models.otp import (
    OTPGenerateRequest,
    OTPSendRequest,
    OTPVerifyRequest,
    OTPGenerateResponse,
    OTPVerifyResponse
)
from app.services.otp_service import otp_service
from app.services.mail_service import mail_service
from app.middleware.rate_limit import is_allowed
import datetime

async def generate_otp(request: OTPGenerateRequest) -> OTPGenerateResponse:
    """Generate OTP code based on user_id and current time"""
    try:
        otp = otp_service.generate_user_otp(request.user_id)
        
        return OTPGenerateResponse(
            status="success",
            message="OTP generated successfully",
            data={
                "user_id": request.user_id,
                "email": request.email,
                "otp": otp,
                "expires_in": 300,
                "valid_window": "5 minutes",
                "timestamp": datetime.datetime.now().isoformat()
            }
        )
    except Exception as e:
        print(f"❌ Generate OTP error: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate OTP")

async def send_otp(request: OTPSendRequest) -> OTPGenerateResponse:
    """Send OTP via email"""
    try:
        await mail_service.send_otp_email(request.email, request.otp, 5)
        
        return OTPGenerateResponse(
            status="success",
            message="OTP sent successfully",
            data={
                "user_id": request.user_id,
                "email": request.email,
                "otp_sent": True,
                "timestamp": datetime.datetime.now().isoformat()
            }
        )
    except Exception as e:
        print(f"❌ Send OTP error: {e}")
        raise HTTPException(status_code=500, detail="Failed to send email")

async def verify_otp(request: OTPVerifyRequest) -> OTPVerifyResponse:
    """Verify OTP code with rate limiting and anti-replay protection"""
    try:
        # ✅ Check rate limit
        if not is_allowed(request.user_id):
            raise HTTPException(
                status_code=429,
                detail={
                    "error": "Rate limit exceeded",
                    "message": "Too many verification attempts. Please wait 1 minute before trying again.",
                    "retry_after": 60,
                    "max_attempts": 5,
                    "window": "1 minute"
                }
            )
        
        # Verify OTP
        result = otp_service.verify_user_otp(request.user_id, request.otp, interval=300)
        
        if result == "valid":
            txn_id = "TXN-" + datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            
            return OTPVerifyResponse(
                status="success",
                message="OTP verified successfully",
                data={
                    "user_id": request.user_id,
                    "email": request.email,
                    "verified": True,
                    "txn_id": txn_id,
                    "timestamp": datetime.datetime.now().isoformat()
                }
            )
        elif result == "expired":
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "OTP expired",
                    "message": "OTP has expired (>5 minutes old). Please generate a new one.",
                    "code": "OTP_EXPIRED"
                }
            )
        elif result == "already_used":
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "OTP already used",
                    "message": "This OTP has already been used. Please generate a new one.",
                    "code": "OTP_ALREADY_USED"
                }
            )
        else:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "Invalid OTP",
                    "message": "The OTP code is incorrect. Please check and try again.",
                    "code": "OTP_INVALID"
                }
            )
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Verify OTP error: {e}")
        raise HTTPException(status_code=500, detail="Verification failed")