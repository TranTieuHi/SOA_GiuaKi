import pymysql
import os
from dotenv import load_dotenv
import time

load_dotenv()

DATABASE_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', 3306)),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': os.getenv('DB_NAME', 'midterm_soa'),
    'charset': 'utf8mb4',
    'autocommit': True,  # ✅ Enable auto-commit
    'connect_timeout': 5,
    'read_timeout': 5,
    'write_timeout': 5
}

print(f"\n{'='*60}")
print(f"🔧 AUTH SERVICE DATABASE CONFIG")
print(f"{'='*60}")
print(f"   Host: {DATABASE_CONFIG['host']}")
print(f"   Port: {DATABASE_CONFIG['port']}")
print(f"   User: {DATABASE_CONFIG['user']}")
print(f"   Database: {DATABASE_CONFIG['database']}")
print(f"   Auto-commit: {DATABASE_CONFIG['autocommit']}")
print(f"{'='*60}\n")

class DatabasePool:
    def __init__(self):
        self.pool = []
        self.max_connections = 5  # ✅ Reduce pool size
        self.connection_timeout = 300  # 5 minutes
        
    def get_connection(self):
        try:
            # ✅ Always create fresh connection for critical operations
            connection = pymysql.connect(**DATABASE_CONFIG)
            
            # ✅ Set isolation level to READ COMMITTED
            with connection.cursor() as cursor:
                cursor.execute("SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED")
                cursor.execute("SET SESSION autocommit = 1")
            
            print(f"🔗 Fresh AUTH database connection created (autocommit: True)")
            return connection
            
        except Exception as e:
            print(f"❌ Auth database connection error: {e}")
            raise e
    
    def return_connection(self, connection):
        # ✅ Always close connection to ensure fresh data
        if connection and connection.open:
            connection.close()
            print(f"🔌 Connection closed to ensure fresh data on next request")

# Global database pool
db = DatabasePool()

def get_db_connection():
    return db.get_connection()

# ✅ Add function to force refresh all connections
def refresh_connections():
    """Force refresh all database connections"""
    global db
    try:
        # Close all pooled connections
        while db.pool:
            conn = db.pool.pop()
            if conn.open:
                conn.close()
        print("🔄 All database connections refreshed")
    except Exception as e:
        print(f"⚠️ Error refreshing connections: {e}")