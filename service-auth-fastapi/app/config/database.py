import pymysql
import os
from dotenv import load_dotenv

load_dotenv()

# ✅ Sử dụng CÙNG DATABASE với Tuition Service
DATABASE_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', 3306)),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': os.getenv('DB_NAME', 'midterm_soa'), 
    'charset': 'utf8mb4',
    'autocommit': False
}

print(f"\n{'='*60}")
print(f"🔧 AUTH SERVICE DATABASE CONFIG")
print(f"{'='*60}")
print(f"   Host: {DATABASE_CONFIG['host']}")
print(f"   Port: {DATABASE_CONFIG['port']}")
print(f"   User: {DATABASE_CONFIG['user']}")
print(f"   Database: {DATABASE_CONFIG['database']}")  # ✅ Should show 'midterm_soa'
print(f"{'='*60}\n")

class DatabasePool:
    def __init__(self):
        self.pool = []
        self.max_connections = 10
        
    def get_connection(self):
        try:
            if self.pool:
                connection = self.pool.pop()
                if connection.open:
                    return connection
            
            # Create new connection
            connection = pymysql.connect(**DATABASE_CONFIG)
            print(f"🔗 New AUTH database connection created (database: {DATABASE_CONFIG['database']})")
            return connection
            
        except Exception as e:
            print(f"❌ Auth database connection error: {e}")
            raise e
    
    def return_connection(self, connection):
        if connection and connection.open:
            if len(self.pool) < self.max_connections:
                self.pool.append(connection)
            else:
                connection.close()

# Global database pool
db = DatabasePool()

def get_db_connection():
    return db.get_connection()