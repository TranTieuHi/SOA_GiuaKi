from fastapi import HTTPException, status, Depends
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

# HTTPBearer for extracting token from Authorization header
security = HTTPBearer(auto_error=False)

def verify_token(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> dict:
    """
    Verify JWT token and extract user information
    
    Args:
        credentials: HTTPAuthorizationCredentials from Authorization header
        
    Returns:
        dict: User information from token payload
        
    Raises:
        HTTPException: If token is invalid, expired, or missing
    """
    # Check if credentials provided
    if credentials is None:
        print("❌ No credentials provided")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "success": False,
                "statusCode": 401,
                "message": "Not authenticated - No token provided",
                "error": "MISSING_TOKEN"
            },
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
                    detail={
                        "success": False,
                        "statusCode": 401,
                        "message": "Token has expired",
                        "error": "TOKEN_EXPIRED"
                    },
                    headers={"WWW-Authenticate": "Bearer"},
                )
        
        # Extract user information
        user_id = payload.get("user_id")
        email = payload.get("email")
        username = payload.get("username")
        role = payload.get("role", "user")  # Default role is 'user'
        
        print(f"👤 User ID: {user_id}")
        print(f"📧 Email: {email}")
        print(f"👔 Role: {role}")
        print(f"{'='*60}\n")
        
        # Validate required fields
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "success": False,
                    "statusCode": 401,
                    "message": "Invalid token - user_id missing",
                    "error": "INVALID_TOKEN_PAYLOAD"
                },
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Return user information
        return {
            "user_id": user_id,
            "email": email,
            "username": username,
            "role": role
        }
        
    except JWTError as e:
        print(f"❌ JWT Error: {type(e).__name__}")
        print(f"❌ Error message: {str(e)}")
        print(f"❌ SECRET_KEY: {SECRET_KEY[:20]}...")
        print(f"{'='*60}\n")
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "success": False,
                "statusCode": 401,
                "message": f"Could not validate credentials: {str(e)}",
                "error": "INVALID_TOKEN"
            },
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
            detail={
                "success": False,
                "statusCode": 500,
                "message": f"Authentication verification failed: {str(e)}",
                "error": "INTERNAL_ERROR"
            }
        )

def get_current_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> dict:
    """
    Get current authenticated user from JWT token
    
    This is a wrapper around verify_token for convenience.
    Use this in route dependencies: Depends(get_current_user)
    
    Returns:
        dict: User information
    """
    return verify_token(credentials)

def require_role(allowed_roles: list):
    """
    Dependency to check if user has required role
    
    Usage:
        @router.delete("/admin/users/{user_id}")
        async def delete_user(
            user_id: str,
            current_user: dict = Depends(get_current_user)
        ):
            if current_user.get("role") not in ["admin"]:
                raise HTTPException(403, "Admin only")
            ...
    
    Args:
        allowed_roles: List of allowed roles (e.g., ["admin", "moderator"])
        
    Returns:
        Dependency function
    """
    def check_role(current_user: dict = Depends(get_current_user)):
        user_role = current_user.get("role", "user")
        
        if user_role not in allowed_roles:
            print(f"⚠️ Access denied: User role '{user_role}' not in {allowed_roles}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "success": False,
                    "statusCode": 403,
                    "message": "You don't have permission to access this resource",
                    "error": "INSUFFICIENT_PERMISSIONS",
                    "required_roles": allowed_roles,
                    "your_role": user_role
                }
            )
        
        return current_user
    
    return check_role

def optional_auth(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> Optional[dict]:
    """
    Optional authentication - returns user if token provided, None otherwise
    
    Useful for endpoints that work differently for authenticated users
    but don't require authentication.
    
    Usage:
        @router.get("/products")
        async def get_products(current_user: Optional[dict] = Depends(optional_auth)):
            if current_user:
                # Show personalized recommendations
                return {"products": [...], "recommended": [...]}
            else:
                # Show generic products
                return {"products": [...]}
    """
    if credentials is None:
        return None
    
    try:
        return verify_token(credentials)
    except HTTPException:
        return None