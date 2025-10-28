from fastapi import APIRouter, Depends, HTTPException
from app.middleware.auth_middleware import get_current_user
from app.config.database import get_db_connection, db
import pymysql

router = APIRouter()

@router.get("/users/me")
async def get_current_user_profile(
    current_user: dict = Depends(get_current_user)
):
    """Get profile of currently authenticated user"""
    connection = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor(pymysql.cursors.DictCursor)
        
        # ✅ FIX: Remove 'role' from SELECT
        cursor.execute(
            """
            SELECT user_id, username, email_address, full_name, available_balance 
            FROM users 
            WHERE user_id = %s
            """,
            (current_user["user_id"],)
        )
        user = cursor.fetchone()
        cursor.close()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return {
            "success": True,
            "statusCode": 200,
            "message": "User profile retrieved",
            "data": {
                "user_id": user["user_id"],
                "username": user["username"],
                "email": user["email_address"],
                "full_name": user["full_name"],
                "available_balance": float(user["available_balance"])
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Get profile error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if connection:
            db.return_connection(connection)

@router.put("/users/me")
async def update_user_profile(
    data: dict,
    current_user: dict = Depends(get_current_user)
):
    """Update user profile"""
    connection = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor(pymysql.cursors.DictCursor)
        
        # Update full_name if provided
        if "full_name" in data:
            cursor.execute(
                "UPDATE users SET full_name = %s WHERE user_id = %s",
                (data["full_name"], current_user["user_id"])
            )
            connection.commit()
        
        cursor.close()
        
        return {
            "success": True,
            "statusCode": 200,
            "message": "Profile updated successfully"
        }
        
    except Exception as e:
        if connection:
            connection.rollback()
        print(f"Update profile error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if connection:
            db.return_connection(connection)