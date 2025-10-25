import pymysql
from pymysql.cursors import DictCursor
from dotenv import load_dotenv
import os

load_dotenv()

class Database:
    def __init__(self):
        self.host = os.getenv("DB_HOST", "localhost")
        self.user = os.getenv("DB_USER", "root")
        self.password = os.getenv("DB_PASSWORD", "Hau0925464587")
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
                autocommit=True
            )
            print("✅ Database connected successfully")
            return self.connection
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            raise

    def get_connection(self):
        """Lấy kết nối hiện tại hoặc tạo mới"""
        if self.connection is None or not self.connection.open:
            self.connect()
        return self.connection

    def close(self):
        """Đóng kết nối"""
        if self.connection and self.connection.open:
            self.connection.close()
            print("🔒 Database connection closed")

# Singleton instance
db = Database()