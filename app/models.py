"""
data model for the application
"""
from app import db
from app.exception import TemplateVariableNotFoundException, TemplateValueNotFoundException


class TemplateValue(db.Model):
    __table_args__ = (db.UniqueConstraint('var_name', 'template_value_set_id'),)

    id = db.Column(db.Integer, primary_key=True)
    var_name = db.Column(db.String(256), index=True)
    value = db.Column(db.String(4096), index=True)

    template_value_set_id = db.Column(db.Integer, db.ForeignKey('template_value_set.id'))
    template_value_set = db.relationship('TemplateValueSet', backref=db.backref('values',
                                                                                cascade="all, delete-orphan",
                                                                                lazy='dynamic'))

    def __init__(self, template_value_set, var_name, value=""):
        self.var_name = var_name
        self.value = value
        self.template_value_set = template_value_set

    def __repr__(self):
        return '<TemplateValue %r>' % self.var_name


class TemplateValueSet(db.Model):
    __table_args__ = (db.UniqueConstraint('name', 'config_template_id'),)

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), index=True)

    config_template_id = db.Column(db.Integer, db.ForeignKey('config_template.id'))
    config_template = db.relationship('ConfigTemplate', backref=db.backref('template_value_sets',
                                                                           cascade="all, delete-orphan",
                                                                           lazy='dynamic'))

    def __init__(self, name, config_template=None):
        self.name = name
        self.config_template = config_template

    def __repr__(self):
        if not self.config_template:
            config_template_name = "None"
        else:
            config_template_name = self.config_template.name

        return '<TemplateValueSet %r (%s) in %s>' % (self.name, self.id, config_template_name)

    def get_template_value_names(self):
        """
        get all template variable names of the Template Value Set

        :return:
        """
        result = []
        for obj in self.values.all():
            result.append(obj.var_name)
        return result

    def get_template_value_by_name(self, var_name):
        """
        get the TemplateValue by name within the configuration template

        :param var_name:
        :return:
        """
        result = TemplateValue.query.filter_by(var_name=var_name, template_value_set=self).first()
        if not result:
            raise TemplateValueNotFoundException("Value for '%s' not found in Template Value Set '%s'" % (var_name,
                                                                                                          self.name))

        return result

    def update_variable_value(self, var_name, value=""):
        """
        add or update a template value for the Template Value set

        :param var_name:
        :param value:
        :return:
        """
        if var_name not in self.get_template_value_names():
            # variable not found, create new one
            new_var = TemplateValue(self, var_name, value)
            db.session.add(new_var)
            db.session.commit()

        else:
            # update existing variable
            tpl_var = TemplateValue.query.filter_by(var_name=var_name, template_value_set=self).first()
            tpl_var.value = value
            db.session.commit()

    def is_value_defined(self, val_name):
        """
        checks if the given variable is defined on the Template Value Set

        :param val_name:
        :return:
        """
        return val_name in self.get_template_value_names()


class TemplateVariable(db.Model):
    __table_args__ = (db.UniqueConstraint('var_name', 'config_template_id'),)

    id = db.Column(db.Integer, primary_key=True)
    var_name = db.Column(db.String(256), index=True)
    description = db.Column(db.String(4096), index=True)

    config_template_id = db.Column(db.Integer, db.ForeignKey('config_template.id'))
    config_template = db.relationship('ConfigTemplate', backref=db.backref('variables',
                                                                           cascade="all, delete-orphan",
                                                                           lazy='dynamic'))

    def __init__(self, config_template, var_name, description=""):
        self.var_name = var_name
        self.description = description
        self.config_template = config_template

    def __repr__(self):
        return '<TemplateVariable %r>' % self.var_name


class ConfigTemplate(db.Model):
    __table_args__ = (db.UniqueConstraint('name', 'project_id'),)

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), index=True)
    template_content = db.Column(db.UnicodeText(), index=True)

    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
    project = db.relationship('Project', backref=db.backref('configtemplates',
                                                            cascade="all, delete-orphan",
                                                            lazy='dynamic'))

    def __init__(self, name, project=None, template_content=""):
        self.name = name
        self.project = project
        self.template_content = template_content

    def __repr__(self):
        if not self.project:
            project_name = "None"

        else:
            project_name = self.project.name

        return '<ConfigTemplate %r (%s) in %s>' % (self.name, self.id, project_name)

    def valid_template_value_set_name(self, template_value_set_name):
        """
        test if the given template value set name is valid within the Configuration Template

        :param template_value_set_name:
        :return: True if valid, otherwise false
        """
        query_result = self.template_value_sets.all()
        valid = True
        for obj in query_result:
            if obj.name == template_value_set_name:
                valid = False
                break

        return valid

    def get_template_variable_names(self):
        """
        get all template variable names of the Config Template

        :return:
        """
        result = []
        for obj in self.variables.all():
            result.append(obj.var_name)
        return result

    def get_template_variable_by_name(self, var_name):
        """
        get a TemplateVariable by name within the configuration template

        :param var_name:
        :return:
        """
        result = TemplateVariable.query.filter_by(var_name=var_name, config_template=self).first()
        if not result:
            raise TemplateVariableNotFoundException("Variable '%s' not found in Template '%s'" % (var_name, self.name))
        return result

    def update_template_variable(self, var_name, description=""):
        """
        add or update a template variable for the Config Template

        :param var_name:
        :param description:
        :return:
        """
        if var_name not in self.get_template_variable_names():
            # variable not found, create new one
            new_var = TemplateVariable(self, var_name, description)
            db.session.add(new_var)
            db.session.commit()

        else:
            # update existing variable
            tpl_var = TemplateVariable.query.filter_by(var_name=var_name, config_template=self).first()
            tpl_var.description = description
            db.session.commit()

    def is_variable_defined(self, var_name):
        """
        checks if the given variable is defined on the template

        :param var_name:
        :return:
        """
        return var_name in self.get_template_variable_names()


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
