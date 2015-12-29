"""
views for the Project data object
"""
import logging
from flask import render_template, url_for, redirect, request, flash
from sqlalchemy.exc import IntegrityError
from app import app, db
from app.forms import ProjectForm
from config import ROOT_URL
from app.models import Project

logger = logging.getLogger()


@app.route(ROOT_URL + "project/")
def view_all_projects():
    """view a list of all Projects

    :return:
    """
    return render_template("project/view_all_projects.html", projects=Project.query.all())


@app.route(ROOT_URL + "project/<int:project_id>")
def view_project(project_id):
    """View a single Project

    :param project_id:
    :return:
    """
    return render_template(
            "project/view_project.html",
            project=Project.query.filter(Project.id == project_id).first_or_404()
    )


@app.route(ROOT_URL + "project/add", methods=["GET", "POST"])
@app.route(ROOT_URL + "project/<int:project_id>/edit", methods=["GET", "POST"])
def edit_project(project_id=None):
    """edit/add a new Project

    :param project_id:
    :return:
    """
    if project_id:
        project = Project.query.get(project_id)

    else:
        project = None

    form = ProjectForm(request.form, project)

    if form.validate_on_submit():
        try:
            created = False
            if not project:
                project = Project(name="")
                created = True

            form.populate_obj(project)
            db.session.add(project)
            db.session.commit()

            if created:
                flash("Project %s successful created" % project.name, "success")

            else:
                flash("Project %s successful saved" % project.name, "success")

            return redirect(url_for("view_project", project_id=project.id))

        except IntegrityError as ex:
            if "UNIQUE constraint failed" in str(ex):
                flash("name already exist, please use another one", "error")

            else:
                flash("Project was not created (unknown error)", "error")
            db.session.rollback()

        except Exception:
            msg = "Project was not created (unknown error)"
            logger.error(msg, exc_info=True)
            flash(msg, "error")

    return render_template("project/edit_project.html", project=project, form=form)


@app.route(ROOT_URL + "project/<int:project_id>/delete", methods=["GET", "POST"])
def delete_project(project_id):
    """delete the Project

    :param project_id:
    :return:
    """
    project = Project.query.filter(Project.id == project_id).first_or_404()

    if request.method == "POST":
        # drop record and add message
        try:
            db.session.delete(project)
            db.session.commit()

        except:
            flash("Project %s was not deleted" % project.name, "error")

        flash("Project %s successful deleted" % project.name, "success")
        return redirect(url_for("view_all_projects"))

    return render_template("project/delete_project.html", project=project)
