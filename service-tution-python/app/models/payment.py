from pydantic import BaseModel, Field
from datetime import datetime
from typing import List

class PaymentRequest(BaseModel):
    """Model cho request thanh toán"""
    student_id: str = Field(..., description="Mã sinh viên cần thanh toán")

    class Config:
        json_schema_extra = {
            "example": {
                "student_id": "ST2025001"
            }
        }

class PaymentResponse(BaseModel):
    """Model cho response thanh toán"""
    success: bool
    message: str
    payment_id: int
    user_id: str
    student_id: str
    payment_date: datetime
    remaining_balance: float

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Successfully paid tuition for Nguyen Van A",
                "payment_id": 1,
                "user_id": "USR1737618000000",
                "student_id": "ST2025001",
                "payment_date": "2025-10-23T12:30:00",
                "remaining_balance": 85000000.0
            }
        }

class PaymentHistoryItem(BaseModel):
    """Model cho 1 item trong lịch sử thanh toán"""
    payment_id: int
    user_id: str
    student_id: str
    payment_date: datetime

    class Config:
        json_schema_extra = {
            "example": {
                "payment_id": 1,
                "user_id": "USR1737618000000",
                "student_id": "ST2025001",
                "payment_date": "2025-10-23T12:30:00"
            }
        }

class PaymentHistoryResponse(BaseModel):
    """Model cho response lịch sử thanh toán"""
    payments: List[PaymentHistoryItem]
    total_count: int

    class Config:
        json_schema_extra = {
            "example": {
                "payments": [
                    {
                        "payment_id": 1,
                        "user_id": "USR1737618000000",
                        "student_id": "ST2025001",
                        "payment_date": "2025-10-23T12:30:00"
                    }
                ],
                "total_count": 1
            }
        }