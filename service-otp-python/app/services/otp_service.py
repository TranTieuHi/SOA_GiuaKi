import random
import string
from datetime import datetime, timedelta
from app.config.database import db
from app.services.mail_service import mail_service
from dotenv import load_dotenv
import os
import pyotp
import base64
import time
from typing import Dict, Optional

load_dotenv()

OTP_LENGTH = int(os.getenv("OTP_LENGTH", 6))
OTP_EXPIRY_MINUTES = int(os.getenv("OTP_EXPIRY_MINUTES", 5))
OTP_MAX_ATTEMPTS = int(os.getenv("OTP_MAX_ATTEMPTS", 3))

# ✅ In-memory storage cho OTP secrets
_otp_storage: Dict[str, str] = {}

# ✅ In-memory storage cho tracking OTP đã sử dụng
_used_otp_tokens: Dict[str, set] = {}

class OTPService:
    
    def generate_otp(self) -> str:
        """Tạo mã OTP ngẫu nhiên"""
        return ''.join(random.choices(string.digits, k=OTP_LENGTH))
    
    async def send_otp(self, email: str) -> dict:
        """Gửi OTP qua email"""
        try:
            connection = db.get_connection()
            
            with connection.cursor() as cursor:
                # Kiểm tra email có tồn tại trong hệ thống không
                cursor.execute("SELECT email_address FROM users WHERE email_address = %s", (email,))
                if not cursor.fetchone():
                    raise Exception("Email not found in system")
                
                # Xóa OTP cũ chưa sử dụng của email này
                cursor.execute("""
                    DELETE FROM otp_codes 
                    WHERE email = %s AND verified = 0
                """, (email,))
                
                # Tạo mã OTP mới
                otp_code = self.generate_otp()
                expires_at = datetime.now() + timedelta(minutes=OTP_EXPIRY_MINUTES)
                
                # Lưu vào database
                cursor.execute("""
                    INSERT INTO otp_codes (email, otp_code, expires_at, attempts, verified)
                    VALUES (%s, %s, %s, %s, %s)
                """, (email, otp_code, expires_at, 0, 0))
                
                # Gửi email
                await mail_service.send_otp_email(email, otp_code, OTP_EXPIRY_MINUTES)
                
                return {
                    "success": True,
                    "message": "OTP sent successfully",
                    "email": email,
                    "expires_at": expires_at
                }
                
        except Exception as e:
            raise Exception(str(e))
    
    def verify_otp(self, email: str, otp_code: str) -> dict:
        """Xác thực mã OTP"""
        try:
            connection = db.get_connection()
            
            with connection.cursor() as cursor:
                # Lấy OTP gần nhất chưa được verify
                cursor.execute("""
                    SELECT * FROM otp_codes 
                    WHERE email = %s AND verified = 0
                    ORDER BY created_at DESC
                    LIMIT 1
                """, (email,))
                
                otp_record = cursor.fetchone()
                
                if not otp_record:
                    raise Exception("No OTP found for this email")
                
                # Kiểm tra hết hạn
                if datetime.now() > otp_record['expires_at']:
                    cursor.execute("""
                        DELETE FROM otp_codes WHERE id = %s
                    """, (otp_record['id'],))
                    raise Exception("OTP has expired")
                
                # Kiểm tra số lần thử
                if otp_record['attempts'] >= OTP_MAX_ATTEMPTS:
                    cursor.execute("""
                        DELETE FROM otp_codes WHERE id = %s
                    """, (otp_record['id'],))
                    raise Exception("Maximum attempts exceeded")
                
                # Kiểm tra mã OTP
                if otp_record['otp_code'] != otp_code:
                    # Tăng số lần thử
                    cursor.execute("""
                        UPDATE otp_codes 
                        SET attempts = attempts + 1 
                        WHERE id = %s
                    """, (otp_record['id'],))
                    
                    remaining_attempts = OTP_MAX_ATTEMPTS - (otp_record['attempts'] + 1)
                    raise Exception(f"Invalid OTP code. {remaining_attempts} attempts remaining")
                
                # OTP đúng - đánh dấu đã verify
                verified_at = datetime.now()
                cursor.execute("""
                    UPDATE otp_codes 
                    SET verified = 1, verified_at = %s 
                    WHERE id = %s
                """, (verified_at, otp_record['id']))
                
                return {
                    "success": True,
                    "message": "OTP verified successfully",
                    "email": email,
                    "verified_at": verified_at
                }
                
        except Exception as e:
            raise Exception(str(e))
    
    def get_user_secret(self, user_id: str) -> str:
        """
        Tạo secret key CỐ ĐỊNH từ user_id
        Cùng user_id → cùng secret → cùng OTP tại cùng thời điểm
        
        Args:
            user_id: User ID
            
        Returns:
            Base32-encoded secret key
        """
        # Chuẩn hóa user_id để secret LUÔN giống nhau
        uid = user_id.strip().upper()
        return base64.b32encode(uid.encode()).decode('utf-8')
    
    def generate_user_otp(self, user_id: str) -> str:
        """
        Generate TOTP cho user dựa trên:
        - Secret key từ user_id (cố định)
        - Thời gian hiện tại của máy
        
        Args:
            user_id: User ID
            
        Returns:
            OTP code (6 digits)
        """
        secret = self.get_user_secret(user_id)
        print(f"[GEN] user='{user_id}' secret={secret} ", end="")
        
        # ✅ Tạo TOTP với secret CỐ ĐỊNH
        totp = pyotp.TOTP(secret, interval=30)  # 30 giây mỗi window
        otp = totp.now()  # OTP dựa trên thời gian hiện tại
        
        print(f"otp={otp}")
        
        return otp
    
    def verify_user_otp(self, user_id: str, token: str, interval: int = 300) -> str:
        """
        Verify TOTP với time tolerance
        
        Args:
            user_id: User ID đã dùng khi generate
            token: OTP token cần verify
            interval: Time tolerance (seconds) - default 300 = 5 phút
            
        Returns:
            "valid" | "expired" | "invalid" | "already_used"
        """
        try:
            # ✅ Lấy secret CỐ ĐỊNH từ user_id
            secret = self.get_user_secret(user_id)
            totp = pyotp.TOTP(secret, interval=30)  # 30-second window
            
            current_time = int(time.time())
            print(f"[VERIFY DEBUG]")
            print(f" user_id: '{user_id}'")
            print(f" secret : {secret}")
            print(f" token  : '{token}'")
            print(f" current_time: {current_time}")
            
            # ✅ Kiểm tra OTP đã được sử dụng chưa (anti-replay)
            global _used_otp_tokens
            if user_id not in _used_otp_tokens:
                _used_otp_tokens[user_id] = set()
            
            if token in _used_otp_tokens[user_id]:
                print(f" 🔒 OTP already used!")
                return "already_used"
            
            # Try multiple time windows (past and future)
            tolerance_windows = 10  # ±10 windows = ±5 minutes với 30s intervals
            
            for i in range(-tolerance_windows, tolerance_windows + 1):
                window_time = current_time + (i * 30)
                expected_otp = totp.at(window_time)
                
                print(f" window {i:+2d}: time={window_time} otp={expected_otp} match={expected_otp == token}")
                
                if expected_otp == token:
                    print(f" ✅ MATCH found at window {i}")
                    
                    # Check if OTP expired (older than interval)
                    time_diff = abs(i * 30)
                    if time_diff > interval:
                        print(f" ⏰ OTP expired: {time_diff}s > {interval}s")
                        return "expired"
                    
                    # ✅ Đánh dấu OTP đã sử dụng
                    _used_otp_tokens[user_id].add(token)
                    
                    # ✅ Cleanup old tokens (giữ tối đa 20 tokens gần nhất)
                    if len(_used_otp_tokens[user_id]) > 20:
                        # Remove oldest tokens
                        tokens_list = list(_used_otp_tokens[user_id])
                        _used_otp_tokens[user_id] = set(tokens_list[-20:])
                    
                    return "valid"
            
            print(f" ❌ NO MATCH found in {tolerance_windows*2+1} windows")
            print("----------")
            return "invalid"
            
        except Exception as e:
            print(f"[VERIFY ERROR] {e}")
            return "invalid"
    
    def get_storage_status(self) -> dict:
        """Get current used OTP tokens status"""
        global _used_otp_tokens
        return {
            "total_users": len(_used_otp_tokens),
            "users": {
                user_id: len(tokens) 
                for user_id, tokens in _used_otp_tokens.items()
            }
        }
    
    def clear_storage(self):
        """Clear all used OTP tokens (admin function)"""
        global _used_otp_tokens
        count = sum(len(tokens) for tokens in _used_otp_tokens.values())
        _used_otp_tokens.clear()
        return count

# Singleton instance
otp_service = OTPService()