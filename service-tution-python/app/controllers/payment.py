from app.config.database import db, get_db_connection
from app.models.payment import PaymentRequest, PaymentResponse
from fastapi import HTTPException, Depends
from app.middleware.auth_middleware import get_current_user
from datetime import datetime
import pymysql

async def pay_tuition(
    request: PaymentRequest,
    current_user: dict = Depends(get_current_user)
) -> PaymentResponse:
    """Pay tuition using optimistic locking (version) with retries"""
    max_retries = 3
    student_id = request.student_id
    user_id = current_user.get("user_id")

    for attempt in range(1, max_retries + 1):
        connection = None
        cursor = None
        try:
            connection = get_db_connection()
            cursor = connection.cursor(pymysql.cursors.DictCursor)

            # Start transaction
            cursor.execute("START TRANSACTION")

            # Read student row (get version)
            cursor.execute(
                "SELECT student_id, tuition_amount, is_payed, IFNULL(version, 0) as version "
                "FROM students WHERE student_id = %s FOR UPDATE",
                (student_id,)
            )
            student = cursor.fetchone()

            if not student:
                cursor.execute("ROLLBACK")
                raise HTTPException(status_code=404, detail="Student not found")

            if student["is_payed"]:
                cursor.execute("ROLLBACK")
                raise HTTPException(status_code=400, detail="Tuition already paid")

            tuition_amount = float(student["tuition_amount"])
            current_version = int(student["version"])

            # Attempt to update student using version check
            cursor.execute(
                "UPDATE students SET is_payed = TRUE, version = version + 1 "
                "WHERE student_id = %s AND version = %s",
                (student_id, current_version)
            )

            if cursor.rowcount == 0:
                # Version changed -> someone else updated. rollback and retry.
                cursor.execute("ROLLBACK")
                if attempt < max_retries:
                    continue
                else:
                    raise HTTPException(status_code=409, detail="Payment conflict, please retry")

            # Deduct user balance atomically (ensure sufficient funds)
            cursor.execute(
                "UPDATE users SET available_balance = available_balance - %s "
                "WHERE user_id = %s AND available_balance >= %s",
                (tuition_amount, user_id, tuition_amount)
            )

            if cursor.rowcount == 0:
                # Insufficient balance or user missing
                cursor.execute("ROLLBACK")
                raise HTTPException(status_code=400, detail="Insufficient balance or user not found")

            # Insert payment record
            cursor.execute(
                "INSERT INTO user_student_payment (user_id, student_id, payment_date) "
                "VALUES (%s, %s, NOW())",
                (user_id, student_id)
            )
            payment_id = cursor.lastrowid

            # Commit transaction
            connection.commit()

            # Format response
            return {
                "success": True,
                "message": "Payment successful",
                "payment_id": payment_id,
                "user_id": user_id,
                "student_id": student_id,
                "payment_date": datetime.now().isoformat(),
                "amount_paid": float(tuition_amount)
            }

        except HTTPException:
            # Known errors: rollback if transaction active, re-raise
            if connection:
                try:
                    connection.rollback()
                except Exception:
                    pass
            raise
        except Exception as e:
            # On DB errors: rollback and either retry (for optimistic conflicts) or raise
            if connection:
                try:
                    connection.rollback()
                except Exception:
                    pass

            # If last attempt, raise as 500
            if attempt == max_retries:
                print(f"❌ Payment error (final): {e}")
                raise HTTPException(status_code=500, detail=f"Payment failed: {str(e)}")
            else:
                # log and retry
                print(f"⚠️ Optimistic lock attempt {attempt} failed: {e} — retrying")
                continue
        finally:
            if cursor:
                try:
                    cursor.close()
                except Exception:
                    pass

# ✅ UPDATED: Get payment history from user_student_payment table
async def get_payment_history(
    current_user: dict = Depends(get_current_user),
    limit: int = 50,
    offset: int = 0
):
    """
    Get payment history for current user
    
    Args:
        current_user: Current authenticated user
        limit: Number of records to return
        offset: Offset for pagination
        
    Returns:
        List of payment records with student info
    """
    try:
        connection = get_db_connection()
        cursor = connection.cursor(pymysql.cursors.DictCursor)
        
        user_id = current_user.get('user_id')
        
        # ✅ Query từ bảng user_student_payment với student info
        query = """
            SELECT 
                usp.payment_id,
                usp.user_id,
                usp.student_id,
                usp.payment_date,
                s.full_name as student_name,
                s.class,
                s.faculty,
                s.semester,
                s.year,
                s.tuition_amount as amount_paid
            FROM user_student_payment usp
            JOIN students s ON usp.student_id = s.student_id
            WHERE usp.user_id = %s
            ORDER BY usp.payment_date DESC
            LIMIT %s OFFSET %s
        """
        
        cursor.execute(query, (user_id, limit, offset))
        payments = cursor.fetchall()
        
        # Get total count
        count_query = "SELECT COUNT(*) as total FROM user_student_payment WHERE user_id = %s"
        cursor.execute(count_query, (user_id,))
        total = cursor.fetchone()['total']
        
        cursor.close()
        connection.close()
        
        # Format dates
        for payment in payments:
            if isinstance(payment['payment_date'], datetime):
                payment['payment_date'] = payment['payment_date'].isoformat()
        
        return {
            "success": True,
            "total": total,
            "limit": limit,
            "offset": offset,
            "data": payments
        }
        
    except Exception as e:
        print(f"❌ Error getting payment history: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get payment history: {str(e)}")

# ✅ UPDATED: Get payment statistics from user_student_payment table
async def get_payment_statistics(
    current_user: dict = Depends(get_current_user)
):
    """Get payment statistics for current user"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor(pymysql.cursors.DictCursor)
        
        user_id = current_user.get('user_id')
        
        # ✅ Get statistics từ user_student_payment và join với students
        query = """
            SELECT 
                COUNT(*) as total_payments,
                SUM(s.tuition_amount) as total_amount,
                MIN(usp.payment_date) as first_payment,
                MAX(usp.payment_date) as last_payment
            FROM user_student_payment usp
            JOIN students s ON usp.student_id = s.student_id
            WHERE usp.user_id = %s
        """
        
        cursor.execute(query, (user_id,))
        stats = cursor.fetchone()
        
        cursor.close()
        connection.close()
        
        # Format dates
        if stats['first_payment'] and isinstance(stats['first_payment'], datetime):
            stats['first_payment'] = stats['first_payment'].isoformat()
        if stats['last_payment'] and isinstance(stats['last_payment'], datetime):
            stats['last_payment'] = stats['last_payment'].isoformat()
        
        # Handle None values
        stats['total_amount'] = float(stats['total_amount'] or 0)
        stats['total_payments'] = int(stats['total_payments'] or 0)
        
        return {
            "success": True,
            "data": stats
        }
        
    except Exception as e:
        print(f"❌ Error getting payment statistics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get statistics: {str(e)}")