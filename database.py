import os
import logging
import time
from pathlib import Path
import sqlalchemy
from sqlalchemy import create_engine, event, exc, text
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.pool import QueuePool

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Get the database URL from environment variable
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    # Try to load from .env.development as a fallback
    env_path = Path('.') / '.env.development'
    if env_path.exists():
        from dotenv import load_dotenv
        load_dotenv(dotenv_path=env_path, override=True)
        DATABASE_URL = os.getenv("DATABASE_URL")
        if DATABASE_URL:
            logger.info("Loaded DATABASE_URL from .env.development")
    
    if not DATABASE_URL:
        error_msg = """
        DATABASE_URL environment variable is not set.
        Please ensure you have a .env.development file with DATABASE_URL
        or set the DATABASE_URL environment variable.
        """
        logger.warning(error_msg)
        # Don't raise an error here, let the application start without a database
        # The application will handle the missing database gracefully
        engine = None
        Session = None
else:
    # Log the first few characters of the DATABASE_URL for debugging
    db_info = DATABASE_URL.split('@')[-1] if DATABASE_URL else 'not set'
    logger.info(f"Connecting to database: ***@{db_info}")

    try:
        # Add connection pool settings
        pool_size = int(os.getenv('DB_POOL_SIZE', '5'))
        max_overflow = int(os.getenv('DB_MAX_OVERFLOW', '10'))
        pool_timeout = int(os.getenv('DB_POOL_TIMEOUT', '30'))
        pool_recycle = int(os.getenv('DB_POOL_RECYCLE', '3600'))  # Recycle connections after 1 hour

        # Create database engine with connection pooling
        engine = create_engine(
            DATABASE_URL,
            poolclass=QueuePool,
            pool_size=pool_size,
            max_overflow=max_overflow,
            pool_timeout=pool_timeout,
            pool_recycle=pool_recycle,
            pool_pre_ping=True,  # Enable connection health checks
            connect_args={
                'connect_timeout': 10,  # 10 second connection timeout
                'options': '-c statement_timeout=30000'  # 30 second statement timeout
            }
        )

        # Add event listeners for connection handling
        @event.listens_for(engine, 'engine_connect')
        def receive_connection(dbapi_connection, connection_record):
            logger.debug("Database connection established")

        @event.listens_for(engine, 'checkout')
        def receive_checkout(dbapi_connection, connection_record, connection_proxy):
            logger.debug("Checking out database connection from pool")

        # Create session factory with error handling
        Session = scoped_session(sessionmaker(
            bind=engine,
            autocommit=False,
            autoflush=False,
            expire_on_commit=False
        ))

        # Test the connection
        with engine.connect() as conn:
            conn.execute(sqlalchemy.text("SELECT 1"))
        logger.info("Successfully connected to the database")

    except Exception as e:
        logger.error(f"Failed to initialize database connection: {str(e)}")
        logger.warning("Application will start without database connection")
        engine = None
        Session = None
    
        # Test the connection and log table information
        with engine.connect() as conn:
            from sqlalchemy import inspect
            inspector = inspect(engine)
            table_names = inspector.get_table_names()
            logger.info(f"Successfully connected to database. Found {len(table_names)} tables.")
            
            if table_names:
                logger.info("Tables in database:" + "\n- " + "\n- ".join(table_names))
            else:
                logger.info("No tables found in the database.")

    except Exception as e:
        logger.error(f"Error connecting to the database: {str(e)}")
        logger.error("Please check your DATABASE_URL and ensure the database is accessible.")
        engine = None
        Session = None
