import os
import logging
from pathlib import Path
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Print debug information
logger.info("===== Starting application =====")
logger.info(f"Current working directory: {os.getcwd()}")
logger.info(f"Python version: {os.sys.version}")

# Load environment variables
env_path = Path('.') / '.env.development'
if env_path.exists():
    logger.info(f"Found .env.development at: {env_path.absolute()}")
    load_dotenv(dotenv_path=env_path, override=True)
    logger.info("Loaded environment variables from .env.development")
else:
    logger.info("No .env.development file found, using environment variables")

# Log environment state
logger.info(f"FLASK_ENV: {os.getenv('FLASK_ENV', 'not set (defaulting to production)')}")
logger.info(f"DATABASE_URL: {'set' if os.getenv('DATABASE_URL') else 'not set'}")

app = Flask(__name__)
table_names = []

# Initialize database connection
try:
    logger.info("Initializing database connection...")
    from database import engine, Session
    from sqlalchemy import inspect
    
    inspector = inspect(engine)
    table_names = inspector.get_table_names()
    logger.info(f"Successfully connected to database. Found tables: {table_names}")
    
except Exception as e:
    logger.error(f"Failed to initialize database: {str(e)}")
    logger.warning("Application will start without database connection")

@app.route('/')
def index():
    try:
        return jsonify({
            "status": "success",
            "tables": table_names,
            "database_connected": bool(table_names)
        })
    except Exception as e:
        logger.error(f"Error in index route: {str(e)}")
        return jsonify({
            "status": "error",
            "message": "An error occurred while processing your request"
        }), 500

@app.route('/health')
def health_check():
    return jsonify({
        "status": "ok",
        "database_connected": bool(table_names)
    })

if __name__ == '__main__':
    port = int(os.getenv("PORT", 5000))
    logger.info(f"Starting Flask development server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=os.getenv('FLASK_DEBUG', 'false').lower() == 'true')
