"""
data model for the application
"""
from slugify import slugify

from app import db
from app.exception import TemplateVariableNotFoundException, TemplateValueNotFoundException


class TemplateValue(db.Model):
    __table_args__ = (db.UniqueConstraint('var_name_slug', 'template_value_set_id'),)

    id = db.Column(db.Integer, primary_key=True)
    var_name_slug = db.Column(
        db.String(256),
        index=True,
        nullable=False
    )
    value = db.Column(db.String(4096), index=True)

    template_value_set_id = db.Column(db.Integer, db.ForeignKey('template_value_set.id'))
    template_value_set = db.relationship('TemplateValueSet', backref=db.backref('values',
                                                                                cascade="all, delete-orphan",
                                                                                lazy='dynamic'))

    @staticmethod
    def convert_variable_name(string):
        """
        convert the given to a valid variable representation
        :param string:
        :return:
        """
        return slugify(string, separator="_")

    @property
    def var_name(self):
        return self.var_name_slug

    @var_name.setter
    def var_name(self, value):
        self.var_name_slug = self.convert_variable_name(value)

    def __init__(self, template_value_set, var_name, value=""):
        self.var_name = var_name
        self.value = value
        self.template_value_set = template_value_set

    def __repr__(self):
        return '<TemplateValue %r>' % self.var_name


class TemplateValueSet(db.Model):
    __table_args__ = (db.UniqueConstraint('hostname', 'config_template_id'),)

    id = db.Column(db.Integer, primary_key=True)
    hostname = db.Column(
        db.String(256),
        index=True,
        nullable=False
    )

    config_template_id = db.Column(db.Integer, db.ForeignKey('config_template.id'))
    config_template = db.relationship('ConfigTemplate', backref=db.backref('template_value_sets',
                                                                           cascade="all, delete-orphan",
                                                                           lazy='dynamic'))

    def __init__(self, hostname, config_template=None):
        self.hostname = hostname
        self.config_template = config_template

        # if a config template is specified during the initial creation of the object, all defined variables are copied
        # to this value set
        if config_template:
            self.copy_variables_from_config_template()

    def __repr__(self):
        if not self.config_template:
            config_template_name = "None"
        else:
            config_template_name = self.config_template.name

        return '<TemplateValueSet %r (%s) in %s>' % (self.hostname, self.id, config_template_name)

    @staticmethod
    def convert_variable_name(string):
        """
        convert the given to a valid variable representation
        :param string:
        :return:
        """
        return slugify(string, separator="_")

    def copy_variables_from_config_template(self):
        """
        this function copies all variables from the parent configuration template object, that is defined in this class
        :return:
        """
        if not self.config_template:
            raise ValueError("Config Template not set within the template value set, copy variable names not possible")

        parent_vars = self.config_template.variables.all()

        # add hostname variable
        self.update_variable_value("hostname", value=self.hostname)

        for tpl_var in parent_vars:
            if self.is_value_defined(tpl_var.var_name):
                old_value = self.get_template_value_by_name_as_string(tpl_var.var_name)
            else:
                old_value = ""

            self.update_variable_value(tpl_var.var_name, value=old_value)

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
        get the TemplateValue by name within the configuration template, otherwise an TemplateValueNotFoundException is
        thrown

        The given var_name is unconditionally converted to a slug string representation, before the query occurs.

        :param var_name:
        :return: the TemplateValue instance of teh variable
        """
        result = TemplateValue.query.filter_by(var_name_slug=var_name, template_value_set=self).first()
        if not result:
            raise TemplateValueNotFoundException("Value for '%s' not found in "
                                                 "Template Value Set '%s'" % (var_name, self.hostname))

        return result

    def get_template_value_by_name_as_string(self, var_name):
        """
        get the variable value as string for the given variable name, otherwise an TemplateValueNotFoundException is
        thrown

        :param var_name:
        :return: string representation of the template value
        """
        return str(self.get_template_value_by_name(var_name).value)

    def update_variable_value(self, var_name, value="", auto_convert_var_name=True):
        """
        add or update a template value for the Template Value set. The var_name parameter is automatically converted to
        a slug string.

        :param var_name:
        :param value:
        :param auto_convert_var_name: enables or disables the automatic conversion of the variable names
        :return:
        """
        # convert string
        if auto_convert_var_name:
            var_name = self.convert_variable_name(var_name)

        if var_name not in self.get_template_value_names():
            # variable not found, create new one (automatic conversion is then enforced)
            var_name = self.convert_variable_name(var_name)
            new_var = TemplateValue(self, var_name, value)
            db.session.add(new_var)
            db.session.commit()

        else:
            # update existing variable
            tpl_var = TemplateValue.query.filter_by(var_name_slug=var_name, template_value_set=self).first()
            tpl_var.value = value
            db.session.commit()

        return var_name

    def is_value_defined(self, val_name):
        """
        checks if the given variable is defined on the Template Value Set

        :param val_name:
        :return:
        """
        return val_name in self.get_template_value_names()


class TemplateVariable(db.Model):
    __table_args__ = (db.UniqueConstraint('var_name_slug', 'config_template_id'),)

    id = db.Column(db.Integer, primary_key=True)
    var_name_slug = db.Column(
        db.String(256),
        index=True,
        nullable=False
    )
    description = db.Column(db.String(4096), index=True)

    config_template_id = db.Column(db.Integer, db.ForeignKey('config_template.id'))
    config_template = db.relationship('ConfigTemplate', backref=db.backref('variables',
                                                                           cascade="all, delete-orphan",
                                                                           lazy='dynamic'))

    @property
    def var_name(self):
        return self.var_name_slug

    @var_name.setter
    def var_name(self, value):
        self.var_name_slug = slugify(value, separator="_")

    def __init__(self, config_template, var_name, description=""):
        self.var_name = var_name
        self.description = description
        self.config_template = config_template

    def __repr__(self):
        return '<TemplateVariable %r>' % self.var_name


class ConfigTemplate(db.Model):
    __table_args__ = (db.UniqueConstraint('name', 'project_id'),)

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(
        db.String(128),
        index=True,
        nullable=False
    )
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

    @staticmethod
    def convert_variable_name(string):
        """
        convert the given to a valid variable representation
        :param string:
        :return:
        """
        return slugify(string, separator="_")

    def valid_template_value_set_name(self, template_value_set_name):
        """
        test if the given template value set name is valid within the Configuration Template

        :param template_value_set_name:
        :return: True if valid, otherwise false
        """
        query_result = self.template_value_sets.all()
        valid = True
        for obj in query_result:
            if obj.hostname == template_value_set_name:
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
        result = TemplateVariable.query.filter_by(var_name_slug=var_name, config_template=self).first()
        if not result:
            raise TemplateVariableNotFoundException("Variable '%s' not found in Template '%s'" % (var_name, self.name))
        return result

    def update_template_variable(self, var_name, description="", auto_convert_var_name=True):
        """
        add or update a template variable for the Config Template

        :param var_name:
        :param description:
        :param auto_convert_var_name: enables or disables the automatic conversion of the variable names
        :return: name of the variable that was updated (automatic conversion)
        """
        # convert string
        if auto_convert_var_name:
            var_name = self.convert_variable_name(var_name)

        if var_name not in self.get_template_variable_names():
            # variable not found, create new one (automatic conversion is then enforced)
            var_name = self.convert_variable_name(var_name)
            new_var = TemplateVariable(self, var_name, description)
            db.session.add(new_var)
            db.session.commit()

        else:
            # update existing variable
            tpl_var = TemplateVariable.query.filter_by(var_name_slug=var_name, config_template=self).first()
            tpl_var.description = description
            db.session.commit()

        return var_name

    def is_variable_defined(self, var_name):
        """
        checks if the given variable is defined on the template

        :param var_name:
        :return:
        """
        return var_name in self.get_template_variable_names()


class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(
        db.String(128),
        index=True,
        unique=True,
        nullable=False
    )

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
