import os
from pathlib import Path
from dotenv import load_dotenv

# Print debug information
print("\n[DEBUG] ===== Starting application =====")
print(f"[DEBUG] Current working directory: {os.getcwd()}")
print(f"[DEBUG] Python version: {os.sys.version}")

# First, try to load environment variables from .env.development if it exists
env_path = Path('.') / '.env.development'
if env_path.exists():
    print(f"[DEBUG] Found .env.development at: {env_path.absolute()}")
    load_dotenv(dotenv_path=env_path, override=True)
    print("[DEBUG] Loaded environment variables from .env.development")
else:
    print("[DEBUG] No .env.development file found")

# Print current environment state
print(f"[DEBUG] FLASK_ENV: {os.getenv('FLASK_ENV', 'not set (defaulting to production)')}")
print(f"[DEBUG] DATABASE_URL: {'set' if os.getenv('DATABASE_URL') else 'not set'}")

# Now import Flask and other dependencies
print("\n[DEBUG] Importing Flask and database...")
from flask import Flask, jsonify
from database import engine, Session
from sqlalchemy import inspect

app = Flask(__name__)

# Initialize database and get table names once when the app starts
inspector = inspect(engine)
table_names = inspector.get_table_names()
print(f"[INFO] Connected to database. Found tables: {table_names}")

@app.route('/')
def index():
    return jsonify({"tables": table_names})

if __name__ == '__main__':
    app.run(debug=True, port=os.getenv("PORT", default=5000))
