from app.config.database import db, get_db_connection
from fastapi import HTTPException
from datetime import datetime
import pymysql
import time

def pay_tuition(payment_data: dict, current_user: dict):
    """
    Pay tuition - Deduct from user balance and update student payment status
    """
    connection = None
    cursor = None
    
    try:
        print(f"\n{'='*70}")
        print(f"💳 PROCESSING PAYMENT")
        print(f"{'='*70}")
        print(f"   User ID: {current_user['user_id']}")
        print(f"   Username: {current_user['username']}")
        print(f"   Student ID: {payment_data.get('student_id')}")
        
        student_id = payment_data.get('student_id')
        if not student_id:
            raise HTTPException(
                status_code=400,
                detail={
                    "success": False,
                    "statusCode": 400,
                    "message": "Student ID is required",
                    "error": "MISSING_STUDENT_ID"
                }
            )
        
        connection = get_db_connection()
        cursor = connection.cursor(pymysql.cursors.DictCursor)
        
        # Start transaction
        connection.begin()
        
        # 1. Get student info and lock row
        print(f"\n📚 Step 1: Fetching student info...")
        cursor.execute(
            """
            SELECT student_id, full_name, class, faculty, semester, 
                   year, tuition_amount, is_payed, version
            FROM students
            WHERE student_id = %s
            FOR UPDATE
            """,
            (student_id,)
        )
        student = cursor.fetchone()
        
        if not student:
            connection.rollback()
            raise HTTPException(
                status_code=404,
                detail={
                    "success": False,
                    "statusCode": 404,
                    "message": f"Student {student_id} not found",
                    "error": "STUDENT_NOT_FOUND"
                }
            )
        
        print(f"   ✅ Student found: {student['full_name']}")
        print(f"   Tuition amount: {student['tuition_amount']:,.0f} VND")
        print(f"   Payment status: {'Paid' if student['is_payed'] else 'Unpaid'}")
        
        # Check if already paid
        if student['is_payed']:
            connection.rollback()
            raise HTTPException(
                status_code=400,
                detail={
                    "success": False,
                    "statusCode": 400,
                    "message": "Student has already paid tuition",
                    "error": "ALREADY_PAID"
                }
            )
        
        tuition_amount = float(student['tuition_amount'])
        
        # 2. Get user balance and lock row
        print(f"\n💰 Step 2: Checking user balance...")
        cursor.execute(
            """
            SELECT user_id, username, email_address, full_name, available_balance
            FROM users
            WHERE user_id = %s
            FOR UPDATE
            """,
            (current_user['user_id'],)
        )
        user = cursor.fetchone()
        
        if not user:
            connection.rollback()
            raise HTTPException(
                status_code=404,
                detail={
                    "success": False,
                    "statusCode": 404,
                    "message": "User not found",
                    "error": "USER_NOT_FOUND"
                }
            )
        
        current_balance = float(user['available_balance'])
        print(f"   Current balance: {current_balance:,.0f} VND")
        print(f"   Required amount: {tuition_amount:,.0f} VND")
        
        # Check sufficient balance
        if current_balance < tuition_amount:
            connection.rollback()
            raise HTTPException(
                status_code=400,
                detail={
                    "success": False,
                    "statusCode": 400,
                    "message": "Insufficient balance",
                    "error": "INSUFFICIENT_BALANCE",
                    "current_balance": current_balance,
                    "required_amount": tuition_amount
                }
            )
        
        # 3. Deduct balance from user
        print(f"\n💸 Step 3: Deducting balance from user...")
        new_balance = current_balance - tuition_amount
        
        cursor.execute(
            """
            UPDATE users
            SET available_balance = %s
            WHERE user_id = %s
            """,
            (new_balance, current_user['user_id'])
        )
        
        print(f"   ✅ Balance deducted: {tuition_amount:,.0f} VND")
        print(f"   New balance: {new_balance:,.0f} VND")
        
        # 4. Update student payment status (with optimistic locking)
        print(f"\n✅ Step 4: Updating student payment status...")
        
        cursor.execute(
            """
            UPDATE students
            SET is_payed = 1,
                created_at = NOW(),
                version = version + 1
            WHERE student_id = %s AND version = %s
            """,
            (student_id, student['version'])
        )
        
        if cursor.rowcount == 0:
            connection.rollback()
            raise HTTPException(
                status_code=409,
                detail={
                    "success": False,
                    "statusCode": 409,
                    "message": "Payment conflict - please try again",
                    "error": "VERSION_CONFLICT"
                }
            )
        
        print(f"   ✅ Student payment status updated")
        
        # 5. Create payment history record
        print(f"\n📝 Step 5: Creating payment history...")
        payment_date = datetime.now()
        
        
        cursor.execute(
            """
            INSERT INTO user_student_payment (user_id, student_id, payment_date)
            VALUES (%s, %s, %s)
            """,
            (current_user['user_id'], student_id, payment_date)
        )
        payment_id = cursor.lastrowid
        print(f" 	 ✅ Payment history created: ID {payment_id}")
        
        # 6. Commit transaction
        print(f"\n💾 Step 6: Committing transaction...")
        connection.commit()
        
        print(f"\n{'='*70}")
        print(f"✅ PAYMENT SUCCESSFUL")
        print(f"{'='*70}")
        print(f"   Payment ID: {payment_id}")
        print(f"   Student: {student['full_name']} ({student_id})")
        print(f"   Amount: {tuition_amount:,.0f} VND")
        print(f"   New balance: {new_balance:,.0f} VND")
        print(f"{'='*70}\n")
        
        return {
            "success": True,
            "statusCode": 200,
            "message": "Payment successful",
            "data": {
                "payment_id": payment_id,
                "student_id": student_id,
                "student_name": student['full_name'],
                "student_class": student['class'],
                "student_faculty": student['faculty'],
                "amount_paid": tuition_amount,
                "payment_date": payment_date.isoformat(),
                "remaining_balance": new_balance
            }
        }
        
    except HTTPException:
        if connection:
            connection.rollback()
        raise
    except Exception as e:
        if connection:
            connection.rollback()
        print(f"\n❌ Payment error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "statusCode": 500,
                "message": "Payment processing failed",
                "error": str(e)
            }
        )
    finally:
        if cursor:
            cursor.close()
        if connection:
            db.return_connection(connection)

def get_payment_history(user_id: str):
    """
    Get payment history for a user
    JOIN with students table to get student details
    """
    connection = None
    cursor = None
    
    try:
        print(f"\n{'='*60}")
        print(f"📋 FETCHING PAYMENT HISTORY")
        print(f"{'='*60}")
        print(f"   User ID: {user_id}")
        
        connection = get_db_connection()
        cursor = connection.cursor(pymysql.cursors.DictCursor)
        
        # Get payment history with student details
        cursor.execute(
            """
            SELECT 
                ph.payment_id,
                ph.user_id,
                ph.student_id,
                ph.payment_date,
                s.full_name as student_name,
                s.class as student_class,
                s.faculty as student_faculty,
                s.semester,
                s.year,
                s.tuition_amount,
                u.username,
                u.full_name as user_full_name
            FROM user_student_payment ph
            INNER JOIN students s ON ph.student_id = s.student_id
            INNER JOIN users u ON ph.user_id = u.user_id
            WHERE ph.user_id = %s
            ORDER BY ph.payment_date DESC
            """,
            (user_id,)
        )
        
        payments = cursor.fetchall()
        
        print(f"   ✅ Found {len(payments)} payment(s)")
        
        result = []
        for payment in payments:
            result.append({
                "payment_id": payment["payment_id"],
                "student_id": payment["student_id"],
                "student_name": payment["student_name"],
                "student_class": payment["student_class"],
                "student_faculty": payment["student_faculty"],
                "semester": payment["semester"],
                "year": payment["year"],
                "amount": float(payment["tuition_amount"] or 0),
                "payment_date": payment["payment_date"].isoformat() if payment["payment_date"] else None,
                "user_id": payment["user_id"],
                "username": payment["username"],
                "user_full_name": payment["user_full_name"]
            })
        
        print(f"{'='*60}\n")
        
        return {
            "success": True,
            "statusCode": 200,
            "message": f"Found {len(result)} payment(s)",
            "data": result
        }
        
    except Exception as e:
        print(f"❌ Get payment history error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "statusCode": 500,
                "message": "Failed to get payment history",
                "error": str(e)
            }
        )
    finally:
        if cursor:
            cursor.close()
        if connection:
            db.return_connection(connection)

# ✅ ADD THIS FUNCTION
def get_all_payment_history():
    """
    Get all payment history (admin function)
    JOIN with students and users tables
    """
    connection = None
    cursor = None
    
    try:
        print(f"\n{'='*60}")
        print(f"📋 FETCHING ALL PAYMENT HISTORY")
        print(f"{'='*60}")
        
        connection = get_db_connection()
        cursor = connection.cursor(pymysql.cursors.DictCursor)
        
        # Get all payment history with student details
        cursor.execute(
            """
            SELECT 
                ph.payment_id,
                ph.user_id,
                ph.student_id,
                ph.payment_date,
                s.full_name as student_name,
                ...
            FROM user_student_payment ph  -- <<< SỬA TÊN BẢNG
            INNER JOIN students s ON ph.student_id = s.student_id
            INNER JOIN users u ON ph.user_id = u.user_id
            WHERE ph.user_id = %s
            ORDER BY ph.payment_date DESC -- <<< SỬA TÊN CỘT
            """,
            (user_id,)
        )
                
        payments = cursor.fetchall()
        
        print(f"   ✅ Found {len(payments)} payment(s)")
        
        result = []
        for payment in payments:
            result.append({
                "payment_id": payment["payment_id"],
                "student_id": payment["student_id"],
                "student_name": payment["student_name"],
                "student_class": payment["student_class"],
                "student_faculty": payment["student_faculty"],
                "semester": payment["semester"],
                "year": payment["year"],
                "amount": float(payment["tuition_amount"]),
                "payment_date": payment["payment_date"].isoformat() if payment["payment_date"] else None,
                "user_id": payment["user_id"],
                "username": payment["username"],
                "user_full_name": payment["user_full_name"]
            })
        
        print(f"{'='*60}\n")
        
        return {
            "success": True,
            "statusCode": 200,
            "message": f"Found {len(result)} payment(s)",
            "data": result
        }
        
    except Exception as e:
        print(f"❌ Get all payment history error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "statusCode": 500,
                "message": "Failed to get payment history",
                "error": str(e)
            }
        )
    finally:
        if cursor:
            cursor.close()
        if connection:
            db.return_connection(connection)

# Thay thế hoàn toàn hàm cũ bằng hàm này
def get_payment_statistics(user_id: str):
    """
    Get payment statistics for a specific user from the payment history.
    """
    connection = None
    cursor = None
    
    try:
        connection = get_db_connection()
        cursor = connection.cursor(pymysql.cursors.DictCursor)
        
        # Câu query mới để lấy thống kê từ lịch sử giao dịch của người dùng
        cursor.execute(
            """
            SELECT 
                COUNT(ph.payment_id) as total_payments,
                SUM(s.tuition_amount) as total_amount,
                MAX(ph.payment_date) as last_payment
            FROM user_student_payment ph
            INNER JOIN students s ON ph.student_id = s.student_id
            WHERE ph.user_id = %s
            """,
            (user_id,)
        )
        stats = cursor.fetchone()
        
        # Xử lý trường hợp người dùng chưa có giao dịch nào
        last_payment_iso = None
        if stats and stats.get("last_payment"):
            last_payment_iso = stats["last_payment"].isoformat()

        return {
            "success": True,
            "statusCode": 200,
            "message": "Payment statistics retrieved successfully",
            "data": {
                "total_payments": stats.get("total_payments") or 0,
                "total_amount": float(stats.get("total_amount") or 0),
                "last_payment": last_payment_iso
            }
        }
        
    except Exception as e:
        print(f"❌ Get payment statistics error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if cursor:
            cursor.close()
        if connection:
            db.return_connection(connection)