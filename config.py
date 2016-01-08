"""
configuration objects for the flask application and all associated components
"""
import os
APP_BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# the entire application is reachable under /ROOT_URL/ (including the static files)
ROOT_URL = "/ncg/"
STATIC_URL_PATH = ROOT_URL + "static"


class DefaultConfig(object):

    # database configuration
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(APP_BASE_DIR, 'app.db')
    TESTING = False

    # forms configuration
    WTF_CSRF_ENABLED = True
    SECRET_KEY = 'just-for-development'


class TestConfig(DefaultConfig):
    """
    Configuration for basic tests
    """
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(APP_BASE_DIR, 'app_test.db')
    TESTING = True


class LiveServerTestConfig(DefaultConfig):
    """
    Configuration of the Live Server test cases
    """
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(APP_BASE_DIR, 'app_livetest.db')
    LIVESERVER_PORT = 11111
    TESTING = True
