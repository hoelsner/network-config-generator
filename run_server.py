#!python3
"""
Run the flask application locally. The configuration is defined using the `APP_SETTINGS` environment variable (defaults
to `config.DefaultConfig`. If you need to enable the Debug mode, set the environment variable `DEBUG_MODE` to 1.
"""
import os
from app import app

if __name__ == '__main__':
    app.run(debug=os.getenv('DEBUG_MODE', False))
