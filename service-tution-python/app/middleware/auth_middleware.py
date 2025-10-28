from fastapi import HTTPException, Depends, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-here")
ALGORITHM = "HS256"

# ✅ Debug log
print(f"\n{'='*70}")
print(f"🔐 JWT CONFIGURATION")
print(f"{'='*70}")
print(f"   Secret Key: {SECRET_KEY[:20]}...{SECRET_KEY[-20:]}")
print(f"   Algorithm: {ALGORITHM}")
print(f"{'='*70}\n")

security = HTTPBearer()

def verify_token(authorization: str = Header(None)) -> dict:
    """
    Verify JWT token from Authorization header
    """
    try:
        if not authorization:
            raise HTTPException(
                status_code=401,
                detail={
                    "success": False,
                    "statusCode": 401,
                    "message": "Authorization header missing",
                    "error": "MISSING_TOKEN"
                }
            )
        
        if not authorization.startswith("Bearer "):
            raise HTTPException(
                status_code=401,
                detail={
                    "success": False,
                    "statusCode": 401,
                    "message": "Invalid authorization header format",
                    "error": "INVALID_TOKEN_FORMAT"
                }
            )
        
        token = authorization.split(" ")[1]
        
        # ✅ Debug log
        print(f"\n🔍 Verifying token:")
        print(f"   Token (first 50 chars): {token[:50]}...")
        print(f"   Secret Key (first 20): {SECRET_KEY[:20]}...")
        
        # Decode JWT token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        user_id = payload.get("user_id")
        username = payload.get("username")
        email = payload.get("email")
        
        if not user_id:
            raise HTTPException(
                status_code=401,
                detail={
                    "success": False,
                    "statusCode": 401,
                    "message": "Invalid token payload",
                    "error": "INVALID_TOKEN"
                }
            )
        
        print(f"✅ Token verified for user: {username} ({user_id})\n")
        
        return {
            "user_id": user_id,
            "username": username,
            "email": email
        }
        
    except JWTError as e:
        print(f"❌ JWT Error: {e}")
        print(f"   Token: {token[:50] if 'token' in locals() else 'N/A'}...")
        print(f"   Secret: {SECRET_KEY[:20]}...")
        raise HTTPException(
            status_code=401,
            detail={
                "success": False,
                "statusCode": 401,
                "message": "Could not validate credentials",
                "error": "JWT_ERROR"
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Auth error: {e}")
        raise HTTPException(
            status_code=401,
            detail={
                "success": False,
                "statusCode": 401,
                "message": "Authentication failed",
                "error": str(e)
            }
        )

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """
    Extract and verify JWT token to get current user
    """
    try:
        token = credentials.credentials
        
        # ✅ Debug log
        print(f"\n🔍 Verifying token (Depends):")
        print(f"   Token (first 50 chars): {token[:50]}...")
        print(f"   Secret Key (first 20): {SECRET_KEY[:20]}...")
        
        # Decode JWT token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        user_id = payload.get("user_id")
        username = payload.get("username")
        email = payload.get("email")
        
        if not user_id:
            raise HTTPException(
                status_code=401,
                detail={
                    "success": False,
                    "statusCode": 401,
                    "message": "Invalid token payload",
                    "error": "INVALID_TOKEN"
                }
            )
        
        print(f"✅ Token verified for user: {username} ({user_id})\n")
        
        return {
            "user_id": user_id,
            "username": username,
            "email": email
        }
        
    except JWTError as e:
        print(f"❌ JWT Error: {e}")
        print(f"   Token: {token[:50] if 'token' in locals() else 'N/A'}...")
        print(f"   Secret: {SECRET_KEY[:20]}...")
        raise HTTPException(
            status_code=401,
            detail={
                "success": False,
                "statusCode": 401,
                "message": "Could not validate credentials",
                "error": "JWT_ERROR"
            }
        )
    except Exception as e:
        print(f"❌ Auth error: {e}")
        raise HTTPException(
            status_code=401,
            detail={
                "success": False,
                "statusCode": 401,
                "message": "Authentication failed",
                "error": str(e)
            }
        )

authenticate_user = get_current_user