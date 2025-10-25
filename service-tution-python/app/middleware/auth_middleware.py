from fastapi import HTTPException, status, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from dotenv import load_dotenv
import os
from datetime import datetime
from typing import Optional

load_dotenv()

SECRET_KEY = os.getenv("JWT_SECRET", "your-secret-key")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")

print(f"🔐 JWT_SECRET loaded: {SECRET_KEY[:20]}...")
print(f"🔐 JWT_ALGORITHM: {ALGORITHM}")

# ✅ Fix: auto_error=False để tự handle error
security = HTTPBearer(auto_error=False)

def verify_token(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)):
    """
    Middleware để verify JWT token
    """
    # ✅ Check nếu không có credentials
    if credentials is None:
        print("❌ No credentials provided")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated - No token provided",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        token = credentials.credentials
        
        print(f"\n{'='*60}")
        print(f"🔑 Received token: {token[:50]}...")
        print(f"🔑 Token length: {len(token)}")
        
        # Decode JWT token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        print(f"✅ Token decoded successfully!")
        print(f"📦 Payload: {payload}")
        
        # Check expiration
        exp = payload.get("exp")
        if exp:
            exp_datetime = datetime.fromtimestamp(exp)
            now = datetime.now()
            print(f"⏰ Token expires at: {exp_datetime}")
            print(f"⏰ Current time: {now}")
            
            if now > exp_datetime:
                print(f"❌ Token expired!")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token has expired",
                    headers={"WWW-Authenticate": "Bearer"},
                )
        
        # Lấy thông tin user
        user_id = payload.get("user_id")
        email = payload.get("email")
        username = payload.get("username")
        
        print(f"👤 User ID: {user_id}")
        print(f"📧 Email: {email}")
        print(f"{'='*60}\n")
        
        # Validate user_id
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token - user_id missing",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return {
            "user_id": user_id,
            "email": email,
            "username": username
        }
        
    except JWTError as e:
        print(f"❌ JWT Error: {type(e).__name__}")
        print(f"❌ Error message: {str(e)}")
        print(f"❌ SECRET_KEY: {SECRET_KEY[:20]}...")
        print(f"{'='*60}\n")
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not validate credentials: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Unexpected error: {type(e).__name__}")
        print(f"❌ Error: {str(e)}")
        print(f"{'='*60}\n")
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Authentication verification failed: {str(e)}"
        )

def optional_verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Optional JWT verification - không bắt buộc phải có token
    Dùng cho các endpoint public nhưng có thể customize cho user đã login
    """
    if not credentials:
        return None
    
    try:
        return verify_token(credentials)
    except:
        return None

# ✅ ADD: Alias function để dùng trong controllers
def get_current_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)):
    """
    Get current authenticated user from JWT token
    
    Usage in controllers:
        async def my_endpoint(current_user: dict = Depends(get_current_user)):
            user_id = current_user["user_id"]
            email = current_user["email"]
    
    Returns:
        dict: {
            "user_id": str,
            "email": str,
            "username": str
        }
    
    Raises:
        HTTPException: 401 if token is invalid or expired
    """
    return verify_token(credentials)