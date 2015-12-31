"""
WTF forms for the web service
"""
from flask_wtf import Form
from wtforms import ValidationError, StringField, TextAreaField
from wtforms.validators import DataRequired
from wtforms.ext.sqlalchemy.orm import model_form
from app import db
from app.models import Project, TemplateValueSet, TemplateVariable


def reserved_template_variable_names(form, field):
    """
    check reserved template variable names
    :param form:
    :param field:
    :return:
    """
    reserved_template_names = [
        # automatically added when creating a template value set (name of the object)
        "hostname",
    ]

    for name in reserved_template_names:
        if field.data == name:
            raise ValidationError("%s is reserved by the application, please choose another one" % name)


class ConfigTemplateForm(Form):
    name = StringField("name", validators=[DataRequired()])
    template_content = TextAreaField("template content")


class EditConfigTemplateValuesForm(Form):
    csv_content = TextAreaField("Template Value Sets")


ProjectForm = model_form(
    Project,
    base_class=Form,
    db_session=db.session,
    exclude_fk=True
)


TemplateValueSetForm = model_form(
    TemplateValueSet,
    base_class=Form,
    db_session=db.session,
    exclude_fk=True,
    exclude=['config_template']
)

TemplateVariableForm = model_form(
    TemplateVariable,
    base_class=Form,
    db_session=db.session,
    exclude_fk=True,
    field_args={
        "var_name_slug": {
            "label": "Variable Name",
            'validators': [reserved_template_variable_names]
        }
    },
    exclude=['config_template']
)
