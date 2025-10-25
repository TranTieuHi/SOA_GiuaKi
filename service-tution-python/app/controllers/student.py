from app.config.database import db
from app.models.student import StudentSearchRequest, StudentResponse, StudentListResponse
from fastapi import HTTPException
from typing import Optional

def search_student(search_params: StudentSearchRequest):
    """Tìm kiếm sinh viên theo student_id hoặc full_name"""
    try:
        connection = db.get_connection()
        
        with connection.cursor() as cursor:
            # Build dynamic query
            query = "SELECT * FROM students WHERE 1=1"
            params = []
            
            if search_params.student_id:
                query += " AND student_id = %s"
                params.append(search_params.student_id)
            
            if search_params.full_name:
                query += " AND full_name LIKE %s"
                params.append(f"%{search_params.full_name}%")
            
            if search_params.semester:
                query += " AND semester = %s"
                params.append(search_params.semester)
            
            if search_params.year:
                query += " AND year = %s"
                params.append(search_params.year)
            
            cursor.execute(query, params)
            student = cursor.fetchone()
            
            if not student:
                raise HTTPException(status_code=404, detail="Student not found")
            
            # Convert dict to StudentResponse
            return StudentResponse(**student)
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error searching student: {e}")
        raise HTTPException(status_code=500, detail="Failed to search student")

def get_all_students():
    """Lấy tất cả sinh viên"""
    try:
        connection = db.get_connection()
        
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM students ORDER BY created_at DESC")
            students = cursor.fetchall()
            
            # Tính tổng số tiền chưa thanh toán
            cursor.execute("""
                SELECT 
                    SUM(tuition_amount) as total_unpaid,
                    COUNT(*) as unpaid_count
                FROM students 
                WHERE is_payed = 0
            """)
            unpaid_stats = cursor.fetchone()
            
            return StudentListResponse(
                students=[StudentResponse(**s) for s in students],
                total_count=len(students),
                total_unpaid_amount=float(unpaid_stats['total_unpaid'] or 0),
                unpaid_count=unpaid_stats['unpaid_count']
            )
            
    except Exception as e:
        print(f"❌ Error getting all students: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve students")

def get_unpaid_students(semester: Optional[str] = None, year: Optional[int] = None):
    """Lấy danh sách sinh viên chưa thanh toán"""
    try:
        connection = db.get_connection()
        
        with connection.cursor() as cursor:
            query = "SELECT * FROM students WHERE is_payed = 0"
            params = []
            
            if semester:
                query += " AND semester = %s"
                params.append(semester)
            
            if year:
                query += " AND year = %s"
                params.append(year)
            
            query += " ORDER BY created_at DESC"
            
            cursor.execute(query, params)
            students = cursor.fetchall()
            
            # Tính tổng tiền chưa thanh toán
            total_unpaid = sum(float(s['tuition_amount']) for s in students)
            
            return StudentListResponse(
                students=[StudentResponse(**s) for s in students],
                total_count=len(students),
                total_unpaid_amount=total_unpaid,
                unpaid_count=len(students)
            )
            
    except Exception as e:
        print(f"❌ Error getting unpaid students: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve unpaid students")