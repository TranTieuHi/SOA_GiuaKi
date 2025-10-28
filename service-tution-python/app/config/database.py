import pymysql
from pymysql.cursors import DictCursor
from dotenv import load_dotenv
import os
from contextlib import contextmanager

load_dotenv()

DB_CONFIG = {
    'host': os.getenv("DB_HOST", "localhost"),
    'user': os.getenv("DB_USER", "root"),
    'password': os.getenv("DB_PASSWORD", ""),
    'database': os.getenv("DB_NAME", "midterm_soa"),
    'port': int(os.getenv("DB_PORT", 3306)),
    'cursorclass': DictCursor,
    'autocommit': False,
    'charset': 'utf8mb4',
}

print(f"🔧 Database config:")
print(f"   Host: {DB_CONFIG['host']}")
print(f"   Database: {DB_CONFIG['database']}")
print(f"   Port: {DB_CONFIG['port']}")

class Database:
    _instance = None
    _connection_pool = []
    _max_pool_size = 10
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        print("✅ Database manager initialized")
    
    def _create_connection(self):
        try:
            connection = pymysql.connect(**DB_CONFIG)
            print(f"🔗 New database connection created")
            return connection
        except Exception as e:
            print(f"❌ Failed to create connection: {e}")
            raise
    
    def get_connection(self):
        while self._connection_pool:
            connection = self._connection_pool.pop()
            try:
                connection.ping(reconnect=False)
                return connection
            except:
                try:
                    connection.close()
                except:
                    pass
        return self._create_connection()
    
    def return_connection(self, connection):
        if connection is None:
            return
        try:
            connection.ping(reconnect=False)
            if len(self._connection_pool) < self._max_pool_size:
                self._connection_pool.append(connection)
            else:
                connection.close()
        except:
            try:
                connection.close()
            except:
                pass
    
    @contextmanager
    def get_db_session(self):
        connection = None
        try:
            connection = self.get_connection()
            yield connection
        except Exception as e:
            if connection:
                try:
                    connection.rollback()
                except:
                    pass
            raise
        finally:
            if connection:
                self.return_connection(connection)

db = Database()

def get_db_connection():
    return db.get_connection()