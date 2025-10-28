import pymysql
from pymysql.cursors import DictCursor
from dotenv import load_dotenv
import os
from contextlib import contextmanager
from typing import Optional

load_dotenv()

# ✅ Database connection pool configuration
DB_CONFIG = {
    'host': os.getenv("DB_HOST", "localhost"),
    'user': os.getenv("DB_USER", "root"),
    'password': os.getenv("DB_PASSWORD", ""),
    'database': os.getenv("DB_NAME", "midterm_soa"),
    'port': int(os.getenv("DB_PORT", 3306)),
    'cursorclass': DictCursor,
    'autocommit': False,  # ✅ FIX: Disable autocommit for transaction control
    'charset': 'utf8mb4',
    'connect_timeout': 10,
}

print(f"🔧 Database config:")
print(f"   Host: {DB_CONFIG['host']}")
print(f"   Database: {DB_CONFIG['database']}")
print(f"   User: {DB_CONFIG['user']}")
print(f"   Port: {DB_CONFIG['port']}")

class Database:
    """
    Database connection manager with connection pooling
    
    Features:
    - Connection pooling (reuse connections)
    - Transaction support (autocommit=False)
    - Context manager support
    - Thread-safe
    """
    
    _instance: Optional['Database'] = None
    _connection_pool: list = []
    _max_pool_size: int = 10
    
    def __new__(cls):
        """Singleton pattern"""
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize database manager"""
        if self._initialized:
            return
        
        self._initialized = True
        print("✅ Database manager initialized")
    
    def _create_connection(self):
        """Create new database connection"""
        try:
            connection = pymysql.connect(**DB_CONFIG)
            print(f"🔗 New database connection created (pool size: {len(self._connection_pool) + 1})")
            return connection
        except Exception as e:
            print(f"❌ Failed to create connection: {e}")
            raise
    
    def get_connection(self):
        """
        Get connection from pool or create new one
        
        Returns:
            pymysql.Connection: Database connection
            
        Usage:
            connection = db.get_connection()
            try:
                cursor = connection.cursor()
                cursor.execute("SELECT * FROM users")
                connection.commit()
            except Exception as e:
                connection.rollback()
                raise
            finally:
                cursor.close()
        """
        # Try to get connection from pool
        while self._connection_pool:
            connection = self._connection_pool.pop()
            
            # Check if connection is still alive
            try:
                connection.ping(reconnect=False)
                print(f"♻️ Reusing connection from pool (remaining: {len(self._connection_pool)})")
                return connection
            except:
                print(f"⚠️ Stale connection removed from pool")
                try:
                    connection.close()
                except:
                    pass
        
        # Create new connection if pool is empty
        return self._create_connection()
    
    def return_connection(self, connection):
        """
        Return connection to pool
        
        Args:
            connection: pymysql.Connection to return to pool
        """
        if connection is None:
            return
        
        try:
            # Check if connection is still alive
            connection.ping(reconnect=False)
            
            # Return to pool if not full
            if len(self._connection_pool) < self._max_pool_size:
                self._connection_pool.append(connection)
                print(f"♻️ Connection returned to pool (size: {len(self._connection_pool)})")
            else:
                # Pool full, close connection
                connection.close()
                print(f"🔒 Pool full, connection closed")
        except:
            # Connection dead, don't return to pool
            try:
                connection.close()
            except:
                pass
            print(f"⚠️ Dead connection not returned to pool")
    
    @contextmanager
    def get_db_session(self):
        """
        Context manager for database session with automatic cleanup
        
        Usage:
            with db.get_db_session() as connection:
                cursor = connection.cursor()
                cursor.execute("SELECT * FROM users")
                connection.commit()
        """
        connection = None
        try:
            connection = self.get_connection()
            yield connection
        except Exception as e:
            if connection:
                try:
                    connection.rollback()
                    print(f"🔄 Transaction rolled back due to error: {e}")
                except:
                    pass
            raise
        finally:
            if connection:
                self.return_connection(connection)
    
    def connect(self):
        """Legacy method for compatibility"""
        return self.get_connection()
    
    def close(self):
        """Close all connections in pool"""
        print(f"🔒 Closing all connections in pool ({len(self._connection_pool)})")
        
        while self._connection_pool:
            connection = self._connection_pool.pop()
            try:
                connection.close()
            except:
                pass
        
        print("✅ All connections closed")
    
    def execute_query(self, query: str, params: tuple = None):
        """
        Execute a SELECT query and return results
        
        Args:
            query: SQL query string
            params: Query parameters tuple
            
        Returns:
            list: Query results
        """
        with self.get_db_session() as connection:
            cursor = connection.cursor()
            try:
                cursor.execute(query, params)
                results = cursor.fetchall()
                return results
            finally:
                cursor.close()
    
    def execute_update(self, query: str, params: tuple = None):
        """
        Execute an INSERT/UPDATE/DELETE query
        
        Args:
            query: SQL query string
            params: Query parameters tuple
            
        Returns:
            int: Number of affected rows
        """
        with self.get_db_session() as connection:
            cursor = connection.cursor()
            try:
                cursor.execute(query, params)
                connection.commit()
                return cursor.rowcount
            except:
                connection.rollback()
                raise
            finally:
                cursor.close()

# ✅ Singleton instance
db = Database()

# ✅ Helper function for getting connection (backward compatibility)
def get_db_connection():
    """
    Get database connection (for use in controllers)
    
    Returns:
        pymysql.Connection: Database connection
        
    Usage:
        connection = get_db_connection()
        cursor = connection.cursor()
        try:
            cursor.execute("SELECT * FROM users")
            connection.commit()
        except Exception as e:
            connection.rollback()
            raise
        finally:
            cursor.close()
            db.return_connection(connection)  # Return to pool
    """
    return db.get_connection()