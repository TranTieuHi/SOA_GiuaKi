import sys
sys.path.append('..')

from app.utils.password_helper import hash_password
from app.config.database import get_db_connection, db
import pymysql

def update_passwords():
    """Update passwords for existing users"""
    
    users = [
        {"username": "johndoe", "password": "password123"},
        {"username": "janedoe", "password": "password456"},
        {"username": "admin", "password": "admin123"}
    ]
    
    connection = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor(pymysql.cursors.DictCursor)
        
        print("=" * 50)
        print("🔒 Updating passwords for existing users...")
        print("=" * 50)
        
        for user in users:
            # Hash password
            password_hash = hash_password(user["password"])
            
            # Update password
            cursor.execute(
                """
                UPDATE users 
                SET password = %s 
                WHERE username = %s
                """,
                (password_hash, user["username"])
            )
            
            if cursor.rowcount > 0:
                print(f"✅ Updated password for: {user['username']}")
            else:
                print(f"⚠️  User not found: {user['username']}")
        
        connection.commit()
        cursor.close()
        
        print("\n🎉 All passwords updated successfully!")
        print("\n📝 Login credentials:")
        print("   - Username: johndoe, Password: password123")
        print("   - Username: janedoe, Password: password456")
        print("   - Username: admin, Password: admin123")
        print("=" * 50)
        
    except Exception as e:
        if connection:
            connection.rollback()
        print(f"❌ Error updating passwords: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        if connection:
            db.return_connection(connection)

if __name__ == "__main__":
    update_passwords()