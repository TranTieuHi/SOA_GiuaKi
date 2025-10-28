from fastapi import APIRouter, Depends
from app.controllers.payment import (
    pay_tuition, 
    get_payment_history, 
    get_all_payment_history,
    get_payment_statistics
)
from app.middleware.auth_middleware import get_current_user

router = APIRouter(prefix="/payments")

@router.post("/pay")
async def pay(
    data: dict,
    current_user: dict = Depends(get_current_user)
):
    """
    Pay tuition
    POST /payments/pay
    Body: {"student_id": "ST2025001"}
    """
    return pay_tuition(data, current_user)

@router.get("/history")
async def history(
    current_user: dict = Depends(get_current_user)
):
    """
    Get payment history for current user
    GET /payments/history
    """
    return get_payment_history(current_user["user_id"])

@router.get("/history/all")
async def all_history(
    current_user: dict = Depends(get_current_user)
):
    """
    Get all payment history (admin)
    GET /payments/history/all
    """
    return get_all_payment_history()

@router.get("/statistics", summary="Get payment statistics")
def statistics(current_user: dict = Depends(get_current_user)):
    """
    Get payment statistics for the currently logged-in user.
    """
    # Lấy user_id từ thông tin người dùng đã xác thực
    user_id = current_user['user_id']
    
    # Truyền user_id vào hàm controller
    return get_payment_statistics(user_id=user_id)