import os
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object(os.getenv('APP_SETTINGS', "config.DefaultConfig"))
db = SQLAlchemy(app)

from app import models
from app import views
