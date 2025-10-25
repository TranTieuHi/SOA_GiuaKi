from passlib.context import CryptContext

# Cấu hình bcrypt context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """
    Hash password sử dụng bcrypt
    
    Args:
        password: Plain text password
        
    Returns:
        Hashed password string
    """
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify password với hashed password
    
    Args:
        plain_password: Plain text password từ user input
        hashed_password: Hashed password từ database
        
    Returns:
        True nếu password khớp, False nếu không
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """
    Alias cho hash_password (tương thích với các framework khác)
    """
    return hash_password(password)