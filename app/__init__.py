import os
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from config import STATIC_URL_PATH

app = Flask(__name__, static_url_path=STATIC_URL_PATH)
app.config.from_object(os.getenv('APP_SETTINGS', "config.DefaultConfig"))
db = SQLAlchemy(app)

from app import models
from app import views
from app.context_processors import inject_all_project_data
