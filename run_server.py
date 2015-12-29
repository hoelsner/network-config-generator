#!python3
"""
Start a local Flask development server. The configuration is defined using the `APP_SETTINGS` environment variable
(defaults to `config.DefaultConfig`, if you need to enable the debug mode, set the environment variable `DEBUG_MODE`
to 1).
"""
import logging
import os

from app import app

if __name__ == '__main__':
    logging_directory = "log"
    debug_mode = os.getenv('DEBUG_MODE', False)

    if not os.path.exists(logging_directory):
        os.mkdir(logging_directory)

    if debug_mode:
        level = logging.DEBUG

    else:
        level = logging.INFO

    logFormatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    logging.basicConfig(filename=os.path.join(logging_directory, 'application.log'), level=level)

    # add console handler
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(logFormatter)
    logging.getLogger().addHandler(stream_handler)

    logging.getLogger().debug("Start debugging...")

    app.run(host='0.0.0.0', debug=debug_mode)
