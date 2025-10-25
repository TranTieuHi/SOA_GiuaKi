from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional

class OTPGenerateRequest(BaseModel):
    """Model cho request tạo OTP"""
    user_id: str = Field(..., description="User ID")
    email: EmailStr = Field(..., description="Email nhận OTP")

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "USR1737618000000",
                "email": "user@example.com"
            }
        }

class OTPSendRequest(BaseModel):
    """Model cho request gửi OTP"""
    user_id: str = Field(..., description="User ID")
    email: EmailStr = Field(..., description="Email nhận OTP")
    otp: str = Field(..., description="Mã OTP cần gửi")

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "USR1737618000000",
                "email": "user@example.com",
                "otp": "123456"
            }
        }

class OTPVerifyRequest(BaseModel):
    """Model cho request xác thực OTP"""
    user_id: str = Field(..., description="User ID")
    email: EmailStr = Field(..., description="Email đã nhận OTP")
    otp: str = Field(..., min_length=6, max_length=6, description="Mã OTP 6 chữ số")

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "USR1737618000000",
                "email": "user@example.com",
                "otp": "123456"
            }
        }

class OTPGenerateResponse(BaseModel):
    """Model cho response tạo/gửi OTP"""
    status: str
    message: str
    data: dict

    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "message": "OTP generated successfully",
                "data": {
                    "user_id": "USR1737618000000",
                    "email": "user@example.com",
                    "otp": "123456",
                    "expires_in": 300,
                    "timestamp": "2025-10-23T12:35:00"
                }
            }
        }

class OTPVerifyResponse(BaseModel):
    """Model cho response xác thực OTP"""
    status: str
    message: str
    data: dict

    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "message": "OTP verified successfully",
                "data": {
                    "user_id": "USR1737618000000",
                    "email": "user@example.com",
                    "verified": True,
                    "txn_id": "TXN-20251023123500",
                    "timestamp": "2025-10-23T12:35:00"
                }
            }
        }

class HealthResponse(BaseModel):
    """Model cho health check"""
    status: str
    timestamp: str
    service: str
    version: str

    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "timestamp": "2025-10-23T12:35:00",
                "service": "OTP Service",
                "version": "1.0.0"
            }
        }