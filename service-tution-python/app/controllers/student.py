from app.config.database import get_db_connection, db
from fastapi import HTTPException
import pymysql

def search_student_by_id(student_id: str):
    """Search student by ID"""
    connection = None
    cursor = None
    
    try:
        print(f"\n{'='*60}")
        print(f"🔍 SEARCHING STUDENT")
        print(f"{'='*60}")
        print(f"📝 Student ID: {student_id}")
        
        connection = get_db_connection()
        cursor = connection.cursor(pymysql.cursors.DictCursor)
        
        # ✅ FIX: Use 'year' instead of 'academic_year'
        cursor.execute(
            """
            SELECT student_id, full_name, class, faculty, semester, 
                   year, tuition_amount, is_payed, created_at, version
            FROM students
            WHERE student_id = %s
            """,
            (student_id,)
        )
        student = cursor.fetchone()
        
        if not student:
            print(f"❌ Student not found: {student_id}")
            print(f"{'='*60}\n")
            raise HTTPException(
                status_code=404,
                detail={
                    "success": False,
                    "statusCode": 404,
                    "message": f"Student with ID {student_id} not found",
                    "error": "STUDENT_NOT_FOUND"
                }
            )
        
        print(f"✅ Student found:")
        print(f"   Name: {student['full_name']}")
        print(f"   Class: {student['class']}")
        print(f"   Faculty: {student['faculty']}")
        print(f"   Year: {student['year']}")
        print(f"   Tuition: {student['tuition_amount']:,.0f} VND")
        print(f"   Paid: {'Yes' if student['is_payed'] else 'No'}")
        print(f"{'='*60}\n")
        
        return {
            "success": True,
            "statusCode": 200,
            "message": "Student found",
            "data": {
                "student_id": student["student_id"],
                "full_name": student["full_name"],
                "class": student["class"],
                "faculty": student["faculty"],
                "semester": student["semester"],
                "year": student["year"],  # ✅ Changed from academic_year
                "tuition_amount": float(student["tuition_amount"]),
                "is_payed": bool(student["is_payed"]),
                "created_at": student["created_at"].isoformat() if student["created_at"] else None,
                "version": student.get("version", 1)
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error searching student: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "statusCode": 500,
                "message": "Internal server error",
                "error": str(e)
            }
        )
    finally:
        if cursor:
            cursor.close()
        if connection:
            db.return_connection(connection)

def get_all_students():
    """Get all students"""
    connection = None
    cursor = None
    
    try:
        connection = get_db_connection()
        cursor = connection.cursor(pymysql.cursors.DictCursor)
        
        # ✅ FIX: Use 'year' instead of 'academic_year'
        cursor.execute(
            """
            SELECT student_id, full_name, class, faculty, semester, 
                   year, tuition_amount, is_payed, created_at, version
            FROM students
            ORDER BY student_id
            """
        )
        students = cursor.fetchall()
        
        # Convert data types
        result = []
        for student in students:
            result.append({
                "student_id": student["student_id"],
                "full_name": student["full_name"],
                "class": student["class"],
                "faculty": student["faculty"],
                "semester": student["semester"],
                "year": student["year"],
                "tuition_amount": float(student["tuition_amount"]),
                "is_payed": bool(student["is_payed"]),
                "created_at": student["created_at"].isoformat() if student["created_at"] else None,
                "version": student.get("version", 1)
            })
        
        return {
            "success": True,
            "statusCode": 200,
            "message": "Students retrieved",
            "data": result
        }
        
    except Exception as e:
        print(f"❌ Error getting students: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if cursor:
            cursor.close()
        if connection:
            db.return_connection(connection)

def get_unpaid_students():
    """Get unpaid students"""
    connection = None
    cursor = None
    
    try:
        connection = get_db_connection()
        cursor = connection.cursor(pymysql.cursors.DictCursor)
        
        # ✅ FIX: Use 'year' instead of 'academic_year'
        cursor.execute(
            """
            SELECT student_id, full_name, class, faculty, semester, 
                   year, tuition_amount, is_payed, created_at, version
            FROM students
            WHERE is_payed = 0
            ORDER BY student_id
            """
        )
        students = cursor.fetchall()
        
        # Convert data types
        result = []
        for student in students:
            result.append({
                "student_id": student["student_id"],
                "full_name": student["full_name"],
                "class": student["class"],
                "faculty": student["faculty"],
                "semester": student["semester"],
                "year": student["year"],
                "tuition_amount": float(student["tuition_amount"]),
                "is_payed": bool(student["is_payed"]),
                "created_at": student["created_at"].isoformat() if student["created_at"] else None,
                "version": student.get("version", 1)
            })
        
        return {
            "success": True,
            "statusCode": 200,
            "message": "Unpaid students retrieved",
            "data": result
        }
        
    except Exception as e:
        print(f"❌ Error getting unpaid students: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if cursor:
            cursor.close()
        if connection:
            db.return_connection(connection)