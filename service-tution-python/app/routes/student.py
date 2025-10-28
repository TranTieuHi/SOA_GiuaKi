from fastapi import APIRouter, Query, Request
from app.controllers.student import search_student_by_id, get_all_students, get_unpaid_students

# ✅ Add prefix here instead of main.py
router = APIRouter(prefix="/students")

@router.get("/search")
async def search_student(
    request: Request,
    student_id: str = Query(..., description="Student ID to search")
):
    """
    Search student by ID
    GET /students/search?student_id=ST2025004
    """
    print(f"\n{'='*70}")
    print(f"📨 INCOMING REQUEST")
    print(f"{'='*70}")
    print(f"   Method: {request.method}")
    print(f"   URL: {request.url}")
    print(f"   Path: {request.url.path}")
    print(f"   Query Params: {dict(request.query_params)}")
    print(f"   Student ID: {student_id}")
    print(f"{'='*70}\n")
    
    return search_student_by_id(student_id)

@router.get("/")
async def get_students():
    """
    Get all students
    GET /students/
    """
    return get_all_students()

@router.get("/unpaid")
async def get_unpaid():
    """
    Get unpaid students
    GET /students/unpaid
    """
    return get_unpaid_students()

@router.get("/search/{student_id}")
async def search_by_path(student_id: str):
    """
    Search student by ID (path parameter)
    GET /students/search/ST2025004
    """
    return search_student_by_id(student_id)