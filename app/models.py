"""
data model for the application
"""
from app import db


class ConfigTemplate(db.Model):
    __table_args__ = (db.UniqueConstraint('name', 'project_id'),)

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), index=True)
    template_content = db.Column(db.UnicodeText(), index=True)

    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
    project = db.relationship('Project', backref=db.backref('configtemplates', lazy='dynamic'))

    def __init__(self, name, template_content=""):
        self.name = name
        self.template_content = template_content

    def __repr__(self):
        return '<ConfigTemplate %r (%s)>' % (self.name, self.id)


class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), index=True, unique=True)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<Project %r>' % self.name

    def valid_config_template_name(self, config_template_name):
        """
        test if the given config template name is valid within the project

        :param config_template_name:
        :return: True if valid, otherwise false
        """
        query_result = self.configtemplates.all()
        valid = True
        for obj in query_result:
            if obj.name == config_template_name:
                valid = False
                break

        return valid
