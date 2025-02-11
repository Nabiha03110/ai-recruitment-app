import psycopg2
from psycopg2.pool import SimpleConnectionPool
import os
import logging
from contextlib import contextmanager, asynccontextmanager
from dotenv import load_dotenv
import asyncpg
from typing import Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Database Configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'database': os.getenv('DB_NAME', 'postgres'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD'),
    'port': int(os.getenv('DB_PORT', 5432))
}

# Create connection pool
connection_pool = SimpleConnectionPool(
    minconn=1,
    maxconn=10,
    **DB_CONFIG
)

# Custom Exceptions
class DatabaseConnectionError(Exception):
    """Raised when database connection fails"""
    pass

class DatabaseQueryError(Exception):
    """Raised when query execution fails"""
    pass

class DatabaseOperationError(Exception):
    """Raised for general database operations failures"""
    pass


# Global connection pool
connection_pool: Optional[asyncpg.pool.Pool] = None

# Initialize connection pool on startup
async def init_pool():
    """
    Initializes the global connection pool on application startup.

    This function creates a connection pool that allows the application to interact 
    with the database. It should be called once during the application's startup.
    """
    global connection_pool
    if connection_pool is None:
        try:
            logger.info("Initializing database connection pool...")
            connection_pool = await asyncpg.create_pool(
                min_size=0,  # Start with one connection
                max_size=10,  # Limit max connections to avoid resource exhaustion
                **DB_CONFIG
            )
            logger.info("Database connection pool initialized successfully.")
        except Exception as e:
            logger.error(f"Error initializing connection pool: {e}")
            raise DatabaseConnectionError("Failed to initialize the database connection pool.") from e
        
async def close_pool():
    """
    Closes the global connection pool on application shutdown.

    This function gracefully shuts down the connection pool and should be called
    during the application's shutdown process.
    """
    global connection_pool
    if connection_pool:
        try:
            logger.info("Closing database connection pool...")
            await connection_pool.close()
            connection_pool = None
            logger.info("Database connection pool closed successfully.")
        except Exception as e:
            logger.error(f"Error closing connection pool: {e}")
            raise DatabaseOperationError("Failed to close the database connection pool.") from e


@asynccontextmanager
async def get_db_connection():
    """
    Provides a database connection from the pool.

    This function yields a connection from the pool for database operations, ensuring
    that the connection is returned to the pool after use.

    Yields:
        asyncpg.Connection: A connection from the pool.
    """
    if connection_pool is None:
        logger.error("Connection pool is not initialized!")
        raise DatabaseConnectionError("Connection pool is not initialized.")
    
    logger.info("Acquiring database connection...")
    connection = await connection_pool.acquire()
    try:
        logger.debug("Database connection acquired.")
        yield connection
    except Exception as e:
        logger.error(f"Error during database operation: {e}")
        raise DatabaseQueryError("An error occurred during a database operation.") from e
    finally:
        await connection_pool.release(connection)
        logger.debug("Database connection released back to the pool.")
# @contextmanager
# def get_db_connection():
#     """
#     Database connection management with error handling.
    
#     Yields:
#         connection: Database connection from the connection pool
        
#     Raises:
#         DatabaseConnectionError: If connection cannot be established
#     """
#     connection = None
#     try:
#         connection = connection_pool.getconn()
#         connection.autocommit = True
#         yield connection
#     except psycopg2.OperationalError as e:
#         logger.error(f"Failed to get database connection: {e}")
#         raise DatabaseConnectionError(f"Cannot establish database connection: {str(e)}")
#     finally:
#         if connection is not None:
#             try:
#                 connection_pool.putconn(connection)
#             except Exception as e:
#                 logger.error(f"Failed to return connection to pool: {e}")

# def get_db_connection():
#     """
#     Create a new database connection.
#     """
#     try:
#         connection = psycopg2.connect(**DB_CONFIG)
#         connection.autocommit = True
#         return connection
#     except psycopg2.Error as e:
#         raise Exception(f"Error connecting to the database: {e}")

def execute_query(connection, query, params=None, fetch_one=True, commit=False):
    """
    Execute database queries with enhanced error handling.
    
    Args:
        connection: Database connection
        query (str): SQL query to execute
        params (tuple, optional): Query parameters
        fetch_one (bool): If True, fetch single row
        commit (bool): If True, commit transaction
        
    Returns:
        Query results
        
    Raises:
        DatabaseConnectionError: For connection issues
        DatabaseQueryError: For query execution issues
        DatabaseOperationError: For other database operations issues
    """
    cursor = None
    try:
        cursor = connection.cursor()
        cursor.execute(query, params or ())
        
        if commit:
            try:
                connection.commit()
            except psycopg2.Error as e:
                connection.rollback()
                logger.error(f"Transaction commit failed: {e}")
                raise DatabaseOperationError(f"Failed to commit transaction: {str(e)}")
        
        result = cursor.fetchone() if fetch_one else cursor.fetchall()
        if result is None and fetch_one:
            return None
        return result

    except psycopg2.OperationalError as e:
        logger.error(f"Database connection error: {e}")
        raise DatabaseConnectionError(f"Database connection failed: {str(e)}")
    
    except psycopg2.DataError as e:
        logger.error(f"Invalid data format: {e}")
        raise DatabaseQueryError(f"Invalid data format: {str(e)}")
    
    except psycopg2.IntegrityError as e:
        logger.error(f"Database integrity error: {e}")
        raise DatabaseOperationError(f"Database constraint violation: {str(e)}")
    
    except Exception as e:
        logger.error(f"Unexpected database error: {e}")
        raise DatabaseOperationError(f"Unexpected error: {str(e)}")
    
    finally:
        if cursor is not None:
            cursor.close()