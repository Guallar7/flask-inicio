import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

# Get the database URL from environment variable
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set.")

import logging
from sqlalchemy import inspect

print("[DEBUG] DATABASE_URL:", DATABASE_URL)
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
engine = create_engine(DATABASE_URL, pool_size=10, max_overflow=0)
Session = scoped_session(sessionmaker(bind=engine))

try:
    inspector = inspect(engine)
    table_names = inspector.get_table_names()
    for table in table_names:
        print(f"[INFO] Table: {table}")
        logging.info(f"Table: {table}")
    if not table_names:
        print("[INFO] No tables found in the database.")
        logging.info("No tables found in the database.")
except Exception as e:
    print(f"[ERROR] Could not retrieve table names: {e}")
    logging.error(f"Could not retrieve table names: {e}")
