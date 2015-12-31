"""
views for the Template Variable data object
"""
import logging
from flask import render_template, url_for, redirect, request, flash, abort
from sqlalchemy.exc import IntegrityError
from app import app, db
from app.models import ConfigTemplate, TemplateVariable
from app.forms import TemplateVariableForm
from config import ROOT_URL

logger = logging.getLogger()


@app.route(ROOT_URL + "template/<int:config_template_id>/variable/<int:template_variable_id>/edit", methods=["GET",
                                                                                                             "POST"])
def edit_template_variable(config_template_id, template_variable_id):
    """edit a Template Variable

    :param config_template_id:
    :param template_variable_id:
    :return:
    """
    config_template = ConfigTemplate.query.filter(ConfigTemplate.id == config_template_id).first_or_404()
    template_variable = TemplateVariable.query.filter(TemplateVariable.id == template_variable_id).first_or_404()
    # edit of the hostname is not permitted
    if template_variable.var_name == "hostname":
        abort(403)

    old_var_name = template_variable.var_name

    form = TemplateVariableForm(request.form, template_variable)

    if form.validate_on_submit():
        try:
            if old_var_name != form.var_name_slug.data:
                config_template.rename_variable(old_var_name, new_name=form.var_name_slug.data)

            # update values from form
            template_variable.description = form.description.data
            template_variable.config_template = config_template

            db.session.add(template_variable)
            db.session.commit()

            flash("Template Variable successful saved", "success")

            return redirect(
                url_for(
                    "view_config_template",
                    project_id=config_template.project.id,
                    config_template_id=config_template.id
                )
            )

        except IntegrityError as ex:
            if "UNIQUE constraint failed" in str(ex):
                flash("name already exist, please use another one", "error")

            else:
                flash("Template variable was not created (unknown error)", "error")
            db.session.rollback()

        except Exception:
            msg = "Template variable was not created (unknown error)"
            logger.error(msg, exc_info=True)
            flash(msg, "error")

    return render_template(
        "template_variable/edit_template_variable.html",
        config_template=config_template,
        template_variable=template_variable,
        form=form
    )
