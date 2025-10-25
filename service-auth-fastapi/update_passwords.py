"""
Script để update password cho users đã có trong database
Chạy 1 lần duy nhất sau khi thêm password hashing
"""

from app.config.database import db
from app.utils.password_helper import hash_password

def update_existing_passwords():
    """Update passwords cho users có sẵn"""
    
    # Danh sách users và password mới
    users_passwords = [
        ('johndoe', 'password123'),
        ('janedoe', 'password456'),
        ('admin', 'admin123')
    ]
    
    try:
        connection = db.get_connection()
        
        with connection.cursor() as cursor:
            for username, plain_password in users_passwords:
                # Hash password
                hashed_password = hash_password(plain_password)
                
                # Update trong database
                cursor.execute("""
                    UPDATE users 
                    SET password = %s 
                    WHERE username = %s
                """, (hashed_password, username))
                
                print(f"✅ Updated password for: {username}")
        
        print("\n🎉 All passwords updated successfully!")
        print("\n📝 Login credentials:")
        for username, password in users_passwords:
            print(f"   - Username: {username}, Password: {password}")
        
    except Exception as e:
        print(f"❌ Error updating passwords: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    print("🔒 Updating passwords for existing users...")
    print("=" * 50)
    update_existing_passwords()