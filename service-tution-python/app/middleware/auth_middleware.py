from fastapi import HTTPException, Depends, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-here")
ALGORITHM = "HS256"

security = HTTPBearer(auto_error=False)

# ✅ Routes that don't require authentication
PUBLIC_ROUTES = [
    "/",
    "/health",
    "/docs",
    "/openapi.json",
    "/redoc"
]

def verify_token(authorization: str = None) -> dict:
    """
    Verify JWT token from Authorization header
    """
    try:
        if not authorization:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "success": False,
                    "statusCode": 401,
                    "message": "Authorization header missing",
                    "error": "MISSING_TOKEN",
                    "redirect": "/login"
                }
            )
        
        if not authorization.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "success": False,
                    "statusCode": 401,
                    "message": "Invalid authorization header format",
                    "error": "INVALID_TOKEN_FORMAT",
                    "redirect": "/login"
                }
            )
        
        token = authorization.split(" ")[1]
        
        # Decode JWT token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        user_id = payload.get("user_id")
        username = payload.get("username")
        email = payload.get("email")
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "success": False,
                    "statusCode": 401,
                    "message": "Invalid token payload",
                    "error": "INVALID_TOKEN",
                    "redirect": "/login"
                }
            )
        
        print(f"✅ Token verified for user: {username} ({user_id})")
        
        return {
            "user_id": user_id,
            "username": username,
            "email": email
        }
        
    except JWTError as e:
        print(f"❌ JWT Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "success": False,
                "statusCode": 401,
                "message": "Token expired or invalid",
                "error": "JWT_ERROR",
                "redirect": "/login"
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Auth error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "success": False,
                "statusCode": 401,
                "message": "Authentication failed",
                "error": str(e),
                "redirect": "/login"
            }
        )

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """
    Extract and verify JWT token to get current user
    Used with FastAPI Depends: current_user = Depends(get_current_user)
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "success": False,
                "statusCode": 401,
                "message": "No authentication credentials provided",
                "error": "NO_CREDENTIALS",
                "redirect": "/login"
            }
        )
    
    return verify_token(f"Bearer {credentials.credentials}")

def require_auth(request: Request):
    """
    Middleware function to check authentication for protected routes
    """
    # Check if route is public
    if request.url.path in PUBLIC_ROUTES:
        return None
    
    # Check for Authorization header
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "success": False,
                "statusCode": 401,
                "message": "Access denied. Please login to continue.",
                "error": "AUTHENTICATION_REQUIRED",
                "redirect": "/login"
            }
        )
    
    # Verify token
    return verify_token(auth_header)

# ✅ Optional: Create dependency for routes that optionally need auth
def get_current_user_optional(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Optional[dict]:
    """
    Get current user if token provided, otherwise return None
    """
    if not credentials:
        return None
    
    try:
        return verify_token(f"Bearer {credentials.credentials}")
    except HTTPException:
        return None