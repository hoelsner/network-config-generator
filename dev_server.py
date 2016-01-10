#!python3
"""
Start a local Flask development server.
---------------------------------------

The configuration is defined using the `APP_SETTINGS` environment variable (defaults to `config.DefaultConfig`, if you
need to enable the debug mode, set the environment variable `DEBUG_MODE` to 1).

"""
import os
from app import app

if __name__ == '__main__':
    debug_mode = os.getenv('DEBUG_MODE', False)
    app.run(host='0.0.0.0', debug=debug_mode)
