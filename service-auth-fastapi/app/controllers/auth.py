from passlib.context import CryptContext
from fastapi import HTTPException
from app.config.database import get_db_connection, db, refresh_connections
from app.utils.jwt_helper import create_access_token
import pymysql
import uuid
from datetime import datetime
from app.models.user import LoginRequest, LoginResponse, RegisterRequest, User

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    # ✅ Truncate password to 72 bytes for bcrypt compatibility
    if len(password.encode('utf-8')) > 72:
        password = password.encode('utf-8')[:72].decode('utf-8')
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    # ✅ Truncate password to 72 bytes for bcrypt compatibility
    if len(plain_password.encode('utf-8')) > 72:
        plain_password = plain_password.encode('utf-8')[:72].decode('utf-8')
    
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        print(f"❌ Password verification error: {e}")
        # Fallback to manual bcrypt verification
        import bcrypt
        try:
            return bcrypt.checkpw(
                plain_password.encode('utf-8'), 
                hashed_password.encode('utf-8')
            )
        except Exception as bcrypt_error:
            print(f"❌ Bcrypt fallback error: {bcrypt_error}")
            return False

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
        
        print(f"\n🔍 Searching for user in database...")
        
        # ✅ Updated SQL query based on new table structure
        cursor.execute(
            """
            SELECT user_id, username, email_address, password, full_name, 
                   phone_number, available_balance, created_at, updated_at
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
        print(f"   Phone: {user.get('phone_number', 'N/A')}")
        print(f"   Full name: {user.get('full_name', 'N/A')}")
        print(f"   Balance: {user['available_balance']:,.0f} VND")
        print(f"   Password hash: {user['password'][:50]}...")
        
        # ✅ Verify password using new function
        print(f"\n🔐 Verifying password...")
        print(f"   Input password: '{credentials.password}'")
        
        is_valid = verify_password(credentials.password, user['password'])
        print(f"   Password valid: {is_valid}")
        
        if not is_valid:
            print(f"❌ INVALID PASSWORD")
            print(f"{'='*70}\n")
            raise HTTPException(
                status_code=401,
                detail={
                    "success": False,
                    "statusCode": 401,
                    "message": "Invalid username or password",
                    "error": "INVALID_PASSWORD"
                }
            )
        
        print(f"✅ PASSWORD VERIFIED!")
        
        # ✅ Create JWT token
        print(f"\n🔑 Creating JWT token...")
        token_data = {
            "user_id": user['user_id'],
            "username": user['username'],
            "email": user['email_address']
        }
        print(f"   Token payload: {token_data}")
        
        access_token = create_access_token(token_data)
        print(f"   Token created: {access_token[:50]}...")
        
        print(f"\n{'='*70}")
        print(f"✅ LOGIN SUCCESSFUL")
        print(f"{'='*70}")
        print(f"   User: {user['full_name']} ({user['username']})")
        print(f"   Email: {user['email_address']}")
        print(f"   Balance: {user['available_balance']:,.0f} VND")
        print(f"{'='*70}\n")
        
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
                phone_number=user.get('phone_number'),
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

# ✅ Constants
INITIAL_BALANCE = 50000000.0  # 50 million VND

def register_user(user_data: RegisterRequest):
    """Register new user"""
    connection = None
    cursor = None
    
    try:
        print(f"\n{'='*70}")
        print(f"📝 REGISTERING NEW USER")
        print(f"{'='*70}")
        print(f"   Username: {user_data.username}")
        print(f"   Email: {user_data.email_address}")
        print(f"   Full Name: {user_data.full_name}")
        print(f"   Phone: {getattr(user_data, 'phone_number', 'N/A')}")
        
        connection = get_db_connection()
        cursor = connection.cursor(pymysql.cursors.DictCursor)
        
        # ✅ Check if user exists (username or email)
        print(f"\n🔍 Checking for existing user...")
        cursor.execute(
            """
            SELECT user_id, username, email_address 
            FROM users 
            WHERE email_address = %s OR username = %s
            """,
            (user_data.email_address, user_data.username)
        )
        existing_user = cursor.fetchone()
        
        if existing_user:
            conflict_field = "email" if existing_user['email_address'] == user_data.email_address else "username"
            print(f"❌ USER ALREADY EXISTS:")
            print(f"   Conflict: {conflict_field}")
            print(f"   Existing user: {existing_user['username']} ({existing_user['email_address']})")
            print(f"{'='*70}\n")
            
            raise HTTPException(
                status_code=400,
                detail={
                    "success": False,
                    "statusCode": 400,
                    "message": f"User with this {conflict_field} already exists",
                    "error": "USER_EXISTS",
                    "conflict_field": conflict_field
                }
            )
        
        print(f"✅ No existing user found - proceeding with registration")
        
        # ✅ Hash password
        print(f"\n🔒 Hashing password...")
        hashed_password = hash_password(user_data.password)
        print(f"   Password hashed: {hashed_password[:50]}...")
        
        # ✅ Generate UUID for user_id
        user_id = str(uuid.uuid4())
        print(f"   Generated User ID: {user_id}")
        
        # ✅ Get current timestamp
        current_time = datetime.now()
        
        # ✅ Start transaction
        print(f"\n💾 Inserting user into database...")
        connection.begin()
        
        # ✅ Insert user with all required fields
        cursor.execute(
            """
            INSERT INTO users (
                user_id, username, email_address, password, full_name, 
                phone_number, available_balance, created_at, updated_at
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                user_id,
                user_data.username,
                user_data.email_address,
                hashed_password,
                user_data.full_name,
                getattr(user_data, 'phone_number', None),  # Optional field
                INITIAL_BALANCE,
                current_time,
                current_time
            )
        )
        
        # ✅ Commit transaction
        connection.commit()
        
        print(f"✅ USER REGISTERED SUCCESSFULLY:")
        print(f"   User ID: {user_id}")
        print(f"   Username: {user_data.username}")
        print(f"   Email: {user_data.email_address}")
        print(f"   Initial Balance: {INITIAL_BALANCE:,.0f} VND")
        print(f"{'='*70}\n")
        
        return {
            "success": True,
            "statusCode": 201,
            "message": "User registered successfully",
            "user": {
                "user_id": user_id,
                "username": user_data.username,
                "email_address": user_data.email_address,
                "full_name": user_data.full_name,
                "phone_number": getattr(user_data, 'phone_number', None),
                "available_balance": INITIAL_BALANCE,
                "created_at": current_time.isoformat()
            }
        }
        
    except HTTPException:
        if connection:
            connection.rollback()
        raise
    except Exception as e:
        if connection:
            connection.rollback()
        print(f"\n❌ REGISTRATION ERROR:")
        print(f"   Type: {type(e).__name__}")
        print(f"   Message: {str(e)}")
        print(f"{'='*70}\n")
        
        import traceback
        traceback.print_exc()
        
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

def get_user_profile(user_id: str):
    """Get user profile by user_id with fresh database connection"""
    connection = None
    cursor = None
    
    try:
        print(f"\n{'='*60}")
        print(f"👤 GETTING USER PROFILE FROM AUTH SERVICE")
        print(f"{'='*60}")
        print(f"   User ID: {user_id}")
        print(f"   Timestamp: {datetime.now().isoformat()}")
        
        # ✅ Force refresh connections before critical read
        refresh_connections()
        
        # ✅ Get fresh connection
        connection = get_db_connection()
        cursor = connection.cursor(pymysql.cursors.DictCursor)
        
        # ✅ Verify database and connection info
        cursor.execute("SELECT DATABASE() as current_db, CONNECTION_ID() as conn_id, NOW() as server_time")
        db_info = cursor.fetchone()
        print(f"   🗄️ Database: {db_info['current_db']}")
        print(f"   🔗 Connection ID: {db_info['conn_id']}")
        print(f"   ⏰ Server time: {db_info['server_time']}")
        
        # ✅ Force fresh read with explicit transaction
        cursor.execute("START TRANSACTION")
        
        query = """
            SELECT user_id, username, email_address, full_name, 
                   phone_number, available_balance, created_at, updated_at
            FROM users 
            WHERE user_id = %s
            FOR UPDATE  
        """
        print(f"   📝 Query: {query.replace('FOR UPDATE', 'FOR UPDATE (fresh read)')}")
        
        cursor.execute(query, (user_id,))
        user = cursor.fetchone()
        
        # ✅ Commit to release lock
        cursor.execute("COMMIT")
        
        if not user:
            print(f"   ❌ User not found in database")
            raise HTTPException(
                status_code=404,
                detail={
                    "success": False,
                    "statusCode": 404,
                    "message": "User not found",
                    "error": "USER_NOT_FOUND"
                }
            )
        
        print(f"   ✅ Fresh user data retrieved:")
        print(f"      Username: {user['username']}")
        print(f"      Full name: {user['full_name']}")
        print(f"      💰 Balance: {user['available_balance']:,.0f} VND")
        print(f"      🕐 Updated at: {user['updated_at']}")
        print(f"      🔄 Data freshness: GUARANTEED FRESH")
        print(f"{'='*60}\n")
        
        return {
            "success": True,
            "statusCode": 200,
            "message": "User profile retrieved with fresh data",
            "user": {
                "user_id": user['user_id'],
                "username": user['username'],
                "email_address": user['email_address'],
                "full_name": user['full_name'],
                "phone_number": user['phone_number'],
                "available_balance": float(user['available_balance']),
                "created_at": user['created_at'].isoformat() if user['created_at'] else None,
                "updated_at": user['updated_at'].isoformat() if user['updated_at'] else None
            },
            # ✅ Add metadata for debugging
            "metadata": {
                "connection_id": db_info['conn_id'],
                "server_time": db_info['server_time'].isoformat(),
                "data_freshness": "guaranteed_fresh"
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Get profile error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "statusCode": 500,
                "message": "Failed to get user profile",
                "error": str(e)
            }
        )
    finally:
        if cursor:
            cursor.close()
        if connection:
            db.return_connection(connection)

# ✅ Add endpoint to force refresh
def force_refresh_user_data(user_id: str):
    """Force refresh user data by clearing all caches"""
    try:
        print(f"🔄 FORCE REFRESHING USER DATA for {user_id}")
        
        # Clear connection pool
        refresh_connections()
        
        # Get fresh data
        return get_user_profile(user_id)
        
    except Exception as e:
        print(f"❌ Force refresh error: {e}")
        raise e

def get_user_profile(user_id: str):
    """Get user profile by user_id"""
    connection = None
    cursor = None
    
    try:
        connection = get_db_connection()
        cursor = connection.cursor(pymysql.cursors.DictCursor)
        
        cursor.execute(
            """
            SELECT user_id, username, email_address, full_name, 
                   phone_number, available_balance, created_at, updated_at
            FROM users 
            WHERE user_id = %s
            """,
            (user_id,)
        )
        user = cursor.fetchone()
        
        if not user:
            raise HTTPException(
                status_code=404,
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
            "message": "User profile retrieved",
            "user": {
                "user_id": user['user_id'],
                "username": user['username'],
                "email_address": user['email_address'],
                "full_name": user['full_name'],
                "phone_number": user['phone_number'],
                "available_balance": float(user['available_balance']),
                "created_at": user['created_at'].isoformat() if user['created_at'] else None,
                "updated_at": user['updated_at'].isoformat() if user['updated_at'] else None
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Get profile error: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "statusCode": 500,
                "message": "Failed to get user profile",
                "error": str(e)
            }
        )
    finally:
        if cursor:
            cursor.close()
        if connection:
            db.return_connection(connection)