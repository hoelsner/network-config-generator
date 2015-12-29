"""
views for the Config Template data object
"""
import logging
from flask import render_template, url_for, redirect, request, flash
from sqlalchemy.exc import IntegrityError
from app import app, db
from app.models import ConfigTemplate, Project
from app.forms import ConfigTemplateForm
from config import ROOT_URL

logger = logging.getLogger()


@app.route(ROOT_URL + "project/<int:project_id>/template/<int:config_template_id>")
def view_config_template(project_id, config_template_id):
    """read-only view of a single Config Template

    :param project_id:
    :param config_template_id:
    :return:
    """
    parent_project = Project.query.filter(Project.id == project_id).first_or_404()
    return render_template(
        "config_template/view_config_template.html",
        project=parent_project,
        config_template=ConfigTemplate.query.filter(ConfigTemplate.id == config_template_id).first_or_404()
    )


@app.route(ROOT_URL + "project/<int:project_id>/configtemplate/add", methods=["GET", "POST"])
@app.route(ROOT_URL + "project/<int:project_id>/configtemplate/<int:config_template_id>/edit", methods=["GET", "POST"])
def edit_config_template(project_id, config_template_id=None):
    """edit/add a new Config Template

    :param project_id:
    :param config_template_id:
    :return:
    """
    parent_project = Project.query.filter(Project.id == project_id).first_or_404()
    if config_template_id:
        config_template = ConfigTemplate.query.get(config_template_id)

    else:
        config_template = None

    form = ConfigTemplateForm(request.form, config_template)

    if form.validate_on_submit():
        try:
            created = False
            if not config_template:
                config_template = ConfigTemplate(name="", project=parent_project)
                created = True

            form.populate_obj(config_template)
            config_template.project = parent_project

            # TODO add variable parsing and remove dummy data
            config_template.update_template_variable("var_1", description="first variable for the template")
            config_template.update_template_variable("var_2")
            config_template.update_template_variable("var_3", description="another description")

            db.session.add(config_template)
            db.session.commit()

            if created:
                flash("Config template successful created", "success")

            else:
                flash("Config template successful saved", "success")

            return redirect(
                url_for(
                    "view_config_template",
                    project_id=project_id,
                    config_template_id=config_template.id
                )
            )

        except IntegrityError as ex:
            if "UNIQUE constraint failed" in str(ex):
                flash("name already exist, please use another one", "error")

            else:
                flash("Config template was not created (unknown error)", "error")
            db.session.rollback()

        except Exception:
            msg = "Config template was not created (unknown error)"
            logger.error(msg, exc_info=True)
            flash(msg, "error")

    return render_template(
        "config_template/edit_config_template.html",
        project_id=project_id,
        config_template=config_template,
        form=form
    )


@app.route(ROOT_URL + "project/<int:project_id>/configtemplate/<int:config_template_id>/delete", methods=["GET", "POST"])
def delete_config_template(project_id, config_template_id):
    """delete the Config Template

    :param project_id:
    :param config_template_id:
    :return:
    """
    Project.query.filter(Project.id == project_id).first_or_404()
    config_template = ConfigTemplate.query.filter(ConfigTemplate.id == config_template_id).first_or_404()

    if request.method == "POST":
        project_id = config_template.project.id
        try:
            db.session.delete(config_template)
            db.session.commit()

        except:
            flash("Config Template %s was not deleted" % config_template.name, "error")

        flash("Config Template %s successful deleted" % config_template.name, "success")
        return redirect(url_for("view_project", project_id=project_id))

    return render_template(
        "config_template/delete_config_template.html",
        project_id=project_id,
        config_template=config_template
    )
