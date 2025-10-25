import pymysql
from pymysql.cursors import DictCursor
from dotenv import load_dotenv
import os

load_dotenv()

class Database:
    def __init__(self):
        self.host = os.getenv("DB_HOST", "localhost")
        self.user = os.getenv("DB_USER", "root")
        self.password = os.getenv("DB_PASSWORD", "")
        self.database = os.getenv("DB_NAME", "midterm_soa")
        self.port = int(os.getenv("DB_PORT", 3306))
        self.connection = None

    def connect(self):
        """Tạo kết nối đến database"""
        try:
            self.connection = pymysql.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                port=self.port,
                cursorclass=DictCursor,
                autocommit=True,
                connect_timeout=5,
                read_timeout=10,
                write_timeout=10,
                charset='utf8mb4'
            )
            print(f"✅ Database connected: {self.database}@{self.host}:{self.port}")
            return self.connection
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            raise

    def get_connection(self):
        """Lấy kết nối hiện tại hoặc tạo mới"""
        try:
            if self.connection is None or not self.connection.open:
                self.connect()
            else:
                # Test connection
                self.connection.ping(reconnect=True)
            
            return self.connection
        except Exception as e:
            print(f"❌ Failed to get database connection: {e}")
            try:
                self.connect()
                return self.connection
            except Exception as reconnect_error:
                print(f"❌ Reconnect failed: {reconnect_error}")
                raise

    def close(self):
        """Đóng kết nối"""
        try:
            if self.connection and self.connection.open:
                self.connection.close()
                print("🔒 Database connection closed")
        except Exception as e:
            print(f"⚠️ Error closing database: {e}")

# Singleton instance
db = Database()

def get_db_connection():
    """
    Helper function to get database connection
    ⚠️ Note: Don't close this connection manually in controllers
    It's managed by the db singleton instance
    """
    return db.get_connection()