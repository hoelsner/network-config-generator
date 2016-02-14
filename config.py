"""
configuration objects for the flask application and all associated components

The entire Flask app configuration is controled by the ```APP_SETTINGS``` environment variable. If this variable
is not set, the DefaultConfig is used.
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

    TFTP_DIRECTORY = os.path.join(APP_BASE_DIR, "share", "tftp")
    FTP_DIRECTORY = os.path.join(APP_BASE_DIR, "share", "ftp")

    # Celery configuration
    CELERY_BROKER_URL = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND = "redis://localhost:6379/0"
    CELERY_ACCEPT_CONTENT = ['json']
    CELERY_TASK_SERIALIZER = 'json'
    CELERY_RESULT_SERIALIZER = 'json'


class ProductionConfig(DefaultConfig):
    """
    configuration for production deployments
    """
    SECRET_KEY = os.getenv('APP_SECRET_KEY', "not set")
    PRODUCTION = True

    TFTP_DIRECTORY = os.path.join("/srv", "tftp")
    FTP_DIRECTORY = os.path.join("/srv", "ftp")


class TestConfig(DefaultConfig):
    """
    configuration for unit tests
    """
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(APP_BASE_DIR, 'app_test.db')
    TESTING = True


class LiveServerTestConfig(DefaultConfig):
    """
    configuration for Live Server tests
    """
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(APP_BASE_DIR, 'app_test.db')
    LIVESERVER_PORT = 11111
    TESTING = True
