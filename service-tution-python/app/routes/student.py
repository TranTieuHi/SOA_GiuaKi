from fastapi import APIRouter, Query
from app.models.student import StudentSearchRequest, StudentResponse, StudentListResponse
from app.controllers import student as student_controller
from app.middleware.auth_middleware import verify_token
from fastapi import Depends
from typing import Optional

router = APIRouter(prefix="/students", tags=["Students"])

@router.get("/search", response_model=StudentResponse, dependencies=[Depends(verify_token)])
async def search_student(
    student_id: Optional[str] = Query(None, description="Mã sinh viên"),
    full_name: Optional[str] = Query(None, description="Tên sinh viên"),
    semester: Optional[str] = Query(None, description="Học kỳ (Fall 2024, Spring 2025)"),
    year: Optional[int] = Query(None, description="Năm học")
):
    """Tìm kiếm sinh viên theo student_id, full_name, semester, hoặc year"""
    search_params = StudentSearchRequest(
        student_id=student_id,
        full_name=full_name,
        semester=semester,
        year=year
    )
    return student_controller.search_student(search_params)

@router.get("/", response_model=StudentListResponse, dependencies=[Depends(verify_token)])
async def get_all_students():
    """Lấy danh sách tất cả sinh viên"""
    return student_controller.get_all_students()

@router.get("/unpaid", response_model=StudentListResponse, dependencies=[Depends(verify_token)])
async def get_unpaid_students(
    semester: Optional[str] = Query(None, description="Học kỳ"),
    year: Optional[int] = Query(None, description="Năm học")
):
    """Lấy danh sách sinh viên chưa thanh toán, có thể filter theo semester/year"""
    return student_controller.get_unpaid_students(semester, year)