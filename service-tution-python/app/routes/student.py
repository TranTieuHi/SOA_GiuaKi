from fastapi import APIRouter, Query, Request, Depends
from app.controllers.student import search_student_by_id, get_all_students, get_unpaid_students
from app.middleware.auth_middleware import get_current_user, get_current_user_optional

router = APIRouter(prefix="/students")

@router.get("/search")
async def search_student(
    request: Request,
    student_id: str = Query(..., description="Student ID to search"),
    current_user: dict = Depends(get_current_user)  # ✅ Require authentication
):
    """
    Search student by ID - PROTECTED ROUTE
    GET /students/search?student_id=ST2025004
    Requires: Authorization: Bearer <token>
    """
    print(f"\n📚 User {current_user['username']} searching for student {student_id}")
    return search_student_by_id(student_id)

@router.get("/")
async def get_students(
    current_user: dict = Depends(get_current_user)  # ✅ Require authentication
):
    """
    Get all students - PROTECTED ROUTE
    GET /students/
    """
    print(f"\n📚 User {current_user['username']} getting all students")
    return get_all_students()

@router.get("/unpaid")
async def get_unpaid(
    current_user: dict = Depends(get_current_user)  # ✅ Require authentication
):
    """
    Get unpaid students - PROTECTED ROUTE
    GET /students/unpaid
    """
    print(f"\n📚 User {current_user['username']} getting unpaid students")
    return get_unpaid_students()

@router.get("/search/{student_id}")
async def search_by_path(
    student_id: str,
    current_user: dict = Depends(get_current_user)  # ✅ Require authentication
):
    """
    Search student by ID (path parameter) - PROTECTED ROUTE
    GET /students/search/ST2025004
    """
    print(f"\n📚 User {current_user['username']} searching for student {student_id}")
    return search_student_by_id(student_id)