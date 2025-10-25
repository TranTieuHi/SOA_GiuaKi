from jose import JWTError, jwt
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

load_dotenv()

SECRET_KEY = os.getenv("JWT_SECRET", "your-secret-key")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
EXPIRES_IN_HOURS = int(os.getenv("JWT_EXPIRES_IN_HOURS", 24))

def create_access_token(data: dict) -> str:
    """Tạo JWT token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=EXPIRES_IN_HOURS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> dict:
    """Xác thực JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError as e:
        raise ValueError(f"Token không hợp lệ hoặc đã hết hạn: {str(e)}")