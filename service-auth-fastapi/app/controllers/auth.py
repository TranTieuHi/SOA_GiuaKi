from app.config.database import db
from app.models.user import User, RegisterRequest, LoginRequest, LoginResponse
from app.utils.jwt_helper import create_access_token
from app.utils.password_helper import hash_password, verify_password
from fastapi import HTTPException, status
import time

def register_user(user_data: RegisterRequest):
    """Đăng ký user mới"""
    try:
        connection = db.get_connection()
        
        with connection.cursor() as cursor:
            # 1. Kiểm tra username đã tồn tại
            cursor.execute(
                "SELECT user_id FROM users WHERE username = %s", 
                (user_data.username,)
            )
            if cursor.fetchone():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "success": False,
                        "statusCode": 400,
                        "message": "Username already exists",
                        "error": "DUPLICATE_USERNAME"
                    }
                )
            
            # 2. Kiểm tra email đã tồn tại
            cursor.execute(
                "SELECT user_id FROM users WHERE email_address = %s", 
                (user_data.email_address,)
            )
            if cursor.fetchone():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "success": False,
                        "statusCode": 400,
                        "message": "Email already exists",
                        "error": "DUPLICATE_EMAIL"
                    }
                )
            
            # 3. Hash password
            hashed_password = hash_password(user_data.password)
            print(f"🔒 Password hashed for user: {user_data.username}")
            
            # 4. Tạo user_id unique
            user_id = f"USR{int(time.time() * 1000)}"
            
            # 5. Insert user mới
            cursor.execute("""
                INSERT INTO users 
                (user_id, username, password, email_address, full_name, phone_number, available_balance)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                user_id,
                user_data.username,
                hashed_password,
                user_data.email_address,
                user_data.full_name,
                user_data.phone_number,
                0.00
            ))
            
            print(f"✅ User registered successfully: {user_id}")
            
            return {
                "success": True,
                "statusCode": 201,
                "message": "User registered successfully",
                "user": {
                    "user_id": user_id,
                    "username": user_data.username,
                    "email_address": user_data.email_address,
                    "full_name": user_data.full_name
                }
            }
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Registration error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "statusCode": 500,
                "message": "Registration failed",
                "error": str(e)
            }
        )

def login_user(credentials: LoginRequest):
    """Đăng nhập user"""
    try:
        connection = db.get_connection()
        
        with connection.cursor() as cursor:
            # 1. Tìm user theo username
            cursor.execute("""
                SELECT 
                    user_id,
                    username,
                    password,
                    email_address,
                    full_name,
                    phone_number,
                    available_balance
                FROM users 
                WHERE username = %s
            """, (credentials.username,))
            
            user = cursor.fetchone()
            
            # 2. Kiểm tra user tồn tại
            if not user:
                print(f"❌ Login failed: User '{credentials.username}' not found")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail={
                        "success": False,
                        "statusCode": 401,
                        "message": "Invalid username or password",
                        "error": "INVALID_CREDENTIALS"
                    }
                )
            
            # 3. Verify password
            if not verify_password(credentials.password, user['password']):
                print(f"❌ Login failed: Invalid password for user '{credentials.username}'")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail={
                        "success": False,
                        "statusCode": 401,
                        "message": "Invalid username or password",
                        "error": "INVALID_CREDENTIALS"
                    }
                )
            
            print(f"✅ Login successful: {user['username']}")
            
            # 4. Tạo JWT token
            token_data = {
                "user_id": user['user_id'],
                "username": user['username'],
                "email": user['email_address']
            }
            access_token = create_access_token(token_data)
            
            # 5. Trả về response
            return LoginResponse(
                success=True,
                statusCode=200,
                message="Login successful",
                token=access_token,
                user=User(
                    user_id=user['user_id'],
                    username=user['username'],
                    email_address=user['email_address'],
                    full_name=user['full_name'],
                    phone_number=user['phone_number'],
                    available_balance=float(user['available_balance'])
                )
            )
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Login error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "statusCode": 500,
                "message": "Login failed",
                "error": str(e)
            }
        )

def get_user_profile(user_id: str):
    """Lấy thông tin profile user"""
    try:
        connection = db.get_connection()
        
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    user_id,
                    username,
                    email_address,
                    full_name,
                    phone_number,
                    available_balance
                FROM users 
                WHERE user_id = %s
            """, (user_id,))
            
            user = cursor.fetchone()
            
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail={
                        "success": False,
                        "statusCode": 404,
                        "message": "User not found",
                        "error": "USER_NOT_FOUND"
                    }
                )
            
            return {
                "success": True,
                "statusCode": 200,
                "user": User(**user)
            }
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Get profile error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "statusCode": 500,
                "message": "Failed to get user profile",
                "error": str(e)
            }
        )