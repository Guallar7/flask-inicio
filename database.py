import os
import logging
from pathlib import Path
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker, scoped_session

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
        logger.info("Loaded DATABASE_URL from .env.development")
    
    if not DATABASE_URL:
        error_msg = """
        DATABASE_URL environment variable is not set.
        Please ensure you have a .env.development file with DATABASE_URL
        or set the DATABASE_URL environment variable.
        """
        logger.error(error_msg)
        raise ValueError(error_msg)

# Log the first few characters of the DATABASE_URL for debugging
# (don't log the full URL as it contains sensitive information)
db_info = DATABASE_URL.split('@')[-1] if DATABASE_URL else 'not set'
logger.info(f"Connecting to database: ***@{db_info}")

try:
    # Create database engine
    engine = create_engine(
        DATABASE_URL,
        pool_size=10,
        max_overflow=0,
        pool_pre_ping=True  # Enable connection health checks
    )
    
    # Create session factory
    Session = scoped_session(sessionmaker(bind=engine))
    
    # Test the connection and log table information
    with engine.connect() as conn:
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
    raise
