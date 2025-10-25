import pymysql
from pymysql.cursors import DictCursor
from dotenv import load_dotenv
import os

load_dotenv()

class Database:
    def __init__(self):
        self.host = os.getenv("DB_HOST", "localhost")
        self.port = int(os.getenv("DB_PORT", 3306))
        self.user = os.getenv("DB_USER", "root")
        self.password = os.getenv("DB_PASSWORD", "")
        self.database = os.getenv("DB_NAME", "midterm_soa")
        self.connection = None

    def get_connection(self):
        """Tạo hoặc trả về connection hiện có"""
        if self.connection is None or not self.connection.open:
            try:
                self.connection = pymysql.connect(
                    host=self.host,
                    port=self.port,
                    user=self.user,
                    password=self.password,
                    database=self.database,
                    cursorclass=DictCursor,
                    autocommit=True,
                    charset='utf8mb4'
                )
                print(f"✅ Database connected: {self.database}@{self.host}:{self.port}")
            except Exception as e:
                print(f"❌ Database connection failed: {e}")
                raise
        return self.connection

    def close(self):
        """Đóng connection"""
        if self.connection and self.connection.open:
            self.connection.close()
            print("🔒 Database connection closed")

# Singleton instance
db = Database()