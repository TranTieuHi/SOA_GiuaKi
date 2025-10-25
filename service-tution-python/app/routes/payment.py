from fastapi import APIRouter, Depends
from app.controllers import payment
from app.middleware.auth_middleware import get_current_user

router = APIRouter()

@router.post("/pay")
async def pay_tuition(
    request: payment.PaymentRequest,
    current_user: dict = Depends(get_current_user)
):
    """Pay tuition for a student"""
    return await payment.pay_tuition(request, current_user)

# ✅ Đảm bảo có 2 routes này
@router.get("/history")
async def get_payment_history(
    limit: int = 50,
    offset: int = 0,
    current_user: dict = Depends(get_current_user)
):
    """Get payment history for current user"""
    return await payment.get_payment_history(current_user, limit, offset)

@router.get("/statistics")
async def get_payment_statistics(
    current_user: dict = Depends(get_current_user)
):
    """Get payment statistics for current user"""
    return await payment.get_payment_statistics(current_user)