import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import os

load_dotenv()

class MailService:
    def __init__(self):
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", 587))
        self.smtp_username = os.getenv("SMTP_USERNAME", "")
        self.smtp_password = os.getenv("SMTP_PASSWORD", "")
        self.from_email = os.getenv("SMTP_FROM_EMAIL", "")
        self.from_name = os.getenv("SMTP_FROM_NAME", "SOA Tuition System")

    async def send_otp_email(self, to_email: str, otp_code: str, expires_in_minutes: int = 5):
        """Gửi email chứa mã OTP"""
        
        # Tạo HTML template
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: #f4f4f4;
                }}
                .content {{
                    background-color: white;
                    padding: 30px;
                    border-radius: 10px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }}
                .header {{
                    text-align: center;
                    color: #2563eb;
                    margin-bottom: 30px;
                }}
                .otp-code {{
                    font-size: 32px;
                    font-weight: bold;
                    color: #2563eb;
                    text-align: center;
                    padding: 20px;
                    background-color: #f0f9ff;
                    border-radius: 8px;
                    letter-spacing: 8px;
                    margin: 20px 0;
                }}
                .warning {{
                    color: #dc2626;
                    font-size: 14px;
                    text-align: center;
                    margin-top: 20px;
                }}
                .footer {{
                    text-align: center;
                    margin-top: 30px;
                    font-size: 12px;
                    color: #666;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="content">
                    <div class="header">
                        <h1>🔐 Xác thực OTP</h1>
                    </div>
                    
                    <p>Xin chào,</p>
                    
                    <p>Bạn đã yêu cầu mã OTP để xác thực tài khoản trên hệ thống Thanh toán học phí SOA.</p>
                    
                    <div class="otp-code">
                        {otp_code}
                    </div>
                    
                    <p>Mã OTP này sẽ hết hạn sau <strong>{expires_in_minutes} phút</strong>.</p>
                    
                    <div class="warning">
                        ⚠️ Không chia sẻ mã này với bất kỳ ai!
                    </div>
                    
                    <p>Nếu bạn không yêu cầu mã này, vui lòng bỏ qua email này.</p>
                    
                    <div class="footer">
                        <p>Email này được gửi tự động, vui lòng không trả lời.</p>
                        <p>&copy; 2025 SOA Tuition Payment System</p>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """

        # Tạo email message
        message = MIMEMultipart("alternative")
        message["Subject"] = f"Mã OTP xác thực - {otp_code}"
        message["From"] = f"{self.from_name} <{self.from_email}>"
        message["To"] = to_email

        # Attach HTML content
        html_part = MIMEText(html_content, "html")
        message.attach(html_part)

        try:
            # Gửi email
            await aiosmtplib.send(
                message,
                hostname=self.smtp_server,
                port=self.smtp_port,
                username=self.smtp_username,
                password=self.smtp_password,
                start_tls=True
            )
            print(f"✅ OTP email sent to {to_email}")
            return True
        except Exception as e:
            print(f"❌ Failed to send OTP email: {e}")
            raise Exception(f"Failed to send email: {str(e)}")

# Singleton instance
mail_service = MailService()