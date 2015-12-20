"""
configuration objects for the flask application and all associated components
"""
import os
APP_BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# the entire application is reachable under /ROOT_URL/ (including the static files)
ROOT_URL = "/ncg/"


class DefaultConfig(object):

    # database configuration
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(APP_BASE_DIR, 'app.db')

    # forms configuration
    WTF_CSRF_ENABLED = True
    SECRET_KEY = 'just-for-development'

    STATIC_URL_PATH = ROOT_URL + "static"
