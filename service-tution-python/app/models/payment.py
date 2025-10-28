from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class PaymentRequest(BaseModel):
    student_id: str

class PaymentResponse(BaseModel):
    success: bool
    statusCode: int
    message: str
    payment_id: str
    student_id: str
    student_name: str
    amount_paid: float
    payment_date: str
    remaining_balance: float
    transaction_id: Optional[str] = None