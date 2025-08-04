from flask import Flask, jsonify
import os

import os
if os.getenv("FLASK_ENV", "production") == "development":
    from dotenv import load_dotenv
    load_dotenv(dotenv_path=".env.development")
    print("[DEBUG] Loaded .env.development for development mode.")

from flask import Flask, jsonify
app = Flask(__name__)

@app.route('/')
def index():
    from database import engine
    from sqlalchemy import inspect
    inspector = inspect(engine)
    table_names = inspector.get_table_names()
    return jsonify({"tables": table_names})

if __name__ == '__main__':
    app.run(debug=True, port=os.getenv("PORT", default=5000))
