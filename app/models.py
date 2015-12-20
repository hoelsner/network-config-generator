"""
data model for the application
"""
from app import db


class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), index=True, unique=True)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<Project %r>' % self.name
