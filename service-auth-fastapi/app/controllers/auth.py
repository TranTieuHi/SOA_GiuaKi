import uuid
from app.config.database import db, get_db_connection
from app.models.user import User, RegisterRequest, LoginRequest, LoginResponse
from app.utils.password_helper import hash_password, verify_password
from app.utils.jwt_helper import create_access_token
from fastapi import HTTPException
import pymysql
import shortuuid

def login_user(credentials: LoginRequest):
    """Authenticate user and return JWT token"""
    connection = None
    cursor = None
    
    try:
        print("\n" + "=" * 70)
        print(f"🔐 LOGIN ATTEMPT")
        print("=" * 70)
        print(f"📝 Username/Email: {credentials.username}")
        print(f"📝 Password length: {len(credentials.password)} chars")
        print("=" * 70)
        
        connection = get_db_connection()
        cursor = connection.cursor(pymysql.cursors.DictCursor)
        
        # ✅ FIX: Remove 'role' from SELECT
        print(f"\n🔍 Searching for user in database...")
        cursor.execute(
            """
            SELECT user_id, username, email_address, password, full_name, available_balance
            FROM users 
            WHERE email_address = %s OR username = %s
            """,
            (credentials.username, credentials.username)
        )
        user = cursor.fetchone()
        
        if not user:
            print(f"❌ USER NOT FOUND")
            print(f"   Searched for: {credentials.username}")
            print("=" * 70 + "\n")
            raise HTTPException(
                status_code=401,
                detail={
                    "success": False,
                    "statusCode": 401,
                    "message": "Invalid username or password",
                    "error": "USER_NOT_FOUND"
                }
            )
        
        print(f"✅ USER FOUND:")
        print(f"   User ID: {user['user_id']}")
        print(f"   Username: {user['username']}")
        print(f"   Email: {user['email_address']}")
        print(f"   Full name: {user.get('full_name', 'N/A')}")
        print(f"   Password hash: {user['password'][:50]}...")
        
        # Verify password
        print(f"\n🔐 Verifying password...")
        print(f"   Input password: '{credentials.password}'")
        print(f"   Stored hash: {user['password']}")
        
        is_valid = verify_password(credentials.password, user['password'])
        print(f"   Result: {'✅ VALID' if is_valid else '❌ INVALID'}")
        
        if not is_valid:
            print(f"\n❌ PASSWORD VERIFICATION FAILED")
            print("=" * 70 + "\n")
            raise HTTPException(
                status_code=401,
                detail={
                    "success": False,
                    "statusCode": 401,
                    "message": "Invalid username or password",
                    "error": "INVALID_PASSWORD"
                }
            )
        
        print(f"\n✅ PASSWORD VERIFIED")
        
        # ✅ FIX: Create JWT token without role
        print(f"\n🔑 Creating JWT token...")
        token_data = {
            "user_id": user['user_id'],
            "username": user['username'],
            "email": user['email_address']
        }
        print(f"   Token payload: {token_data}")
        
        access_token = create_access_token(token_data)
        print(f"   Token created: {access_token[:50]}...")
        
        print(f"\n✅ LOGIN SUCCESSFUL")
        print("=" * 70 + "\n")
        
        return LoginResponse(
            success=True,
            statusCode=200,
            message="Login successful",
            token=access_token,
            user=User(
                user_id=user['user_id'],
                username=user['username'],
                email_address=user['email_address'],
                full_name=user.get('full_name'),
                available_balance=float(user['available_balance'])
            )
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR:")
        print(f"   Type: {type(e).__name__}")
        print(f"   Message: {str(e)}")
        print("=" * 70 + "\n")
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


INITIAL_BALANCE = 50000000.0
def register_user(user_data: RegisterRequest):
    """Register new user"""
    connection = None
    cursor = None
    
    try:
        connection = get_db_connection()
        cursor = connection.cursor(pymysql.cursors.DictCursor)
        
        # Check if user exists
        cursor.execute(
            "SELECT user_id FROM users WHERE email_address = %s OR username = %s",
            (user_data.email_address, user_data.username) # ✅ SỬA LỖI 1
        )
        existing_user = cursor.fetchone()
        
        if existing_user:
            raise HTTPException(
                status_code=400,
                detail={
                    "success": False,
                    "statusCode": 400,
                    "message": "Username or email already exists",
                    "error": "USER_EXISTS"
                }
            )
        
        # Hash password
        hashed_password = hash_password(user_data.password)
        
        # Generate user_id
        user_id = shortuuid.uuid()
        print(user_id) # Ví dụ: 'vytxeo5qRAvV3h8v2wP6pE'

        # Bạn có thể tự set độ dài nếu muốn, nhưng sẽ tăng rủi ro trùng lặp
        shortuuid.set_alphabet("abcdefghijklmnopqrstuvwxyz0123456789")
        user_id_10_chars = shortuuid.random(length=10)
        print(user_id_10_chars) # Ví dụ: 'd4r8z1x9k0'
        
        # Start transaction
        connection.begin()
        
        cursor.execute(
            """
            INSERT INTO users (user_id, username, email_address, password, full_name, available_balance)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (user_id, user_data.username, user_data.email_address, hashed_password, 
             user_data.full_name, INITIAL_BALANCE) # ✅ SỬA LỖI 2 và dùng hằng số
        )
        
        # Commit transaction
        connection.commit()
        
        print(f"✅ User registered: {user_data.username} (ID: {user_id})")
        
        return {
            "success": True,
            "statusCode": 201,
            "message": "User registered successfully",
            "user": {
                "user_id": user_id,
                "username": user_data.username,
                "email_address": user_data.email_address # ✅ SỬA LỖI 3 (để nhất quán)
            }
        }
        
    except HTTPException:
        if connection:
            connection.rollback()
        raise
    except Exception as e:
        if connection:
            connection.rollback()
        print(f"❌ Register error: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "statusCode": 500,
                "message": "Registration failed",
                "error": str(e)
            }
        )
    finally:
        if cursor:
            cursor.close()
        if connection:
            db.return_connection(connection)