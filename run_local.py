#!python3
"""
Start a local Flask server.
---------------------------

Run a local instance of the Flask web service using a SQLite database.

"""
import os
from app import app, db

if __name__ == '__main__':
    print("Initialize database...")
    debug_mode = os.getenv('DEBUG_MODE', False)
    db.create_all()
    print("Start the Network Configuration Generator on port 5000...")
    app.run(host='0.0.0.0', debug=debug_mode)
