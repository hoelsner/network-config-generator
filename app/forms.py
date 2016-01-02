"""
WTF forms for the web service
"""
from flask_wtf import Form
from wtforms import ValidationError, StringField, TextAreaField
from wtforms.validators import DataRequired
from wtforms.ext.sqlalchemy.orm import model_form
from app import db
from app.models import Project, TemplateValueSet, TemplateVariable
from app.utils import MakoConfigGenerator
from app.utils.confgen import TemplateSyntaxException


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


def verify_template_syntax(form, field):
    """
    This function verifies the template syntax by creating a dummy template result
    :return:
    """
    template_string = field.data

    # create MakoConfigGenerator instance and parse the template with dummy values
    dcg = MakoConfigGenerator(template_string=template_string)
    for var in dcg.template_variables:
        dcg.set_variable_value(variable=var, value="test")

    try:
        dcg.get_rendered_result()

    except TemplateSyntaxException as ex:
        raise ValidationError("Invalid template, please correct the following error: %s" % str(ex))


class ConfigTemplateForm(Form):
    name = StringField("name", validators=[DataRequired()])
    template_content = TextAreaField("template content", validators=[verify_template_syntax])


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
