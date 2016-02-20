"""
views for the Config Template data object
"""
import csv
import logging
import io
from flask import render_template, url_for, redirect, request, flash, jsonify
from sqlalchemy.exc import IntegrityError
from app import app, db
from app.models import ConfigTemplate, Project, TemplateValueSet
from app.forms import ConfigTemplateForm, EditConfigTemplateValuesForm
from app.utils.appliance import get_local_ip_addresses, verify_appliance_status
from app.utils.export import get_appliance_ftp_password
from app.tasks import update_local_ftp_configurations, update_local_tftp_configurations
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
def add_config_template(project_id):
    """add a new Config Template

    :param project_id:
    :return:
    """
    parent_project = Project.query.filter(Project.id == project_id).first_or_404()

    form = ConfigTemplateForm(request.form)

    if form.validate_on_submit():
        try:
            config_template = ConfigTemplate(name="", project=parent_project)

            config_template.name = form.name.data
            config_template.template_content = form.template_content.data
            config_template.project = parent_project

            db.session.add(config_template)
            db.session.commit()

            flash("Config template <strong>%s</strong> successful created" % config_template.name, "success")

            return redirect(
                url_for(
                    "view_config_template",
                    project_id=project_id,
                    config_template_id=config_template.id
                )
            )

        except IntegrityError as ex:
            if "UNIQUE constraint failed" in str(ex):
                msg = "Config Template name already in use, please use another one"

            else:
                msg = "Config template was not created (unknown error, see log for details)"

            logger.error(msg, exc_info=True)
            flash(msg, "error")
            db.session.rollback()

        except Exception:
            msg = "Config template was not created (unknown error, see log for details)"
            logger.error(msg, exc_info=True)
            flash(msg, "error")

    return render_template(
        "config_template/add_config_template.html",
        project_id=project_id,
        project=parent_project,
        form=form
    )


@app.route(ROOT_URL + "project/<int:project_id>/configtemplate/<int:config_template_id>/edit", methods=["GET", "POST"])
def edit_config_template(project_id, config_template_id):
    """edit a Config Template

    :param project_id:
    :param config_template_id:
    :return:
    """
    parent_project = Project.query.filter(Project.id == project_id).first_or_404()
    config_template = ConfigTemplate.query.filter(ConfigTemplate.id == config_template_id).first_or_404()

    form = ConfigTemplateForm(request.form, config_template)

    if form.validate_on_submit():
        try:
            if form.template_content.data != config_template.template_content:
                flash("Config Template content changed, all Template Value Sets are deleted.", "warning")

            config_template.name = form.name.data
            config_template.template_content = form.template_content.data
            config_template.project = parent_project

            db.session.add(config_template)
            db.session.commit()

            flash("Config template <strong>%s</strong> successful saved" % config_template.name, "success")

            return redirect(
                url_for(
                    "view_config_template",
                    project_id=project_id,
                    config_template_id=config_template.id
                )
            )

        except IntegrityError as ex:
            if "UNIQUE constraint failed" in str(ex):
                msg = "Config Template name already in use, please use another one"

            else:
                msg = "Config template was not created (unknown error, see log for details)"

            logger.error(msg, exc_info=True)
            flash(msg, "error")
            db.session.rollback()

        except Exception:
            msg = "Config template was not created (unknown error, see log for details)"
            logger.error(msg, exc_info=True)
            flash(msg, "error")

    return render_template(
        "config_template/edit_config_template.html",
        project_id=project_id,
        config_template=config_template,
        project=parent_project,
        form=form
    )


@app.route(
    ROOT_URL + "project/<int:project_id>/configtemplate/<int:config_template_id>/edit_all",
    methods=["GET", "POST"]
)
def edit_all_config_template_values(project_id, config_template_id):
    """edit all Config Template Values based on a CSV textarea

    :param project_id:
    :param config_template_id:
    :return:
    """
    Project.query.filter(Project.id == project_id).first_or_404()
    config_template = ConfigTemplate.query.filter(ConfigTemplate.id == config_template_id).first_or_404()

    form = EditConfigTemplateValuesForm(request.form, config_template)

    # hostname is defined in every Template Value Set
    variable_list = [
        "hostname"
    ]
    for var in config_template.variables.all():
        # hostname must be located as first entry
        if var.var_name != "hostname":
            variable_list.append(var.var_name)

    if form.validate_on_submit():
        # update values from the CSV file
        reader = csv.DictReader(io.StringIO(form.csv_content.data), delimiter=";")
        csv_lines = form.csv_content.data.splitlines()
        counter = 0
        for line in reader:
            if "hostname" in line.keys():
                if line["hostname"] is None:
                    flash("Invalid Hostname for Template Value Set: '%s'" % csv_lines[counter], "error")

                elif line["hostname"] == "":
                    flash("No Hostname defined for Template Value Set: '%s'" % form.csv_content.data.splitlines()[counter], "error")

                else:
                    # try to access an existing TemplateValueSet
                    tvs = TemplateValueSet.query.filter(
                        TemplateValueSet.config_template_id == config_template_id,
                        TemplateValueSet.hostname == line["hostname"]
                    ).first()
                    if not tvs:
                        # element not found, create and add a flush message
                        tvs = TemplateValueSet(hostname=line["hostname"], config_template=config_template)
                        flash("Create new Template Value Set for hostname <strong>%s</strong>" % line["hostname"], "success")

                    # update variable values
                    for var in variable_list:
                        if var in line.keys():
                            if line[var]:
                                tvs.update_variable_value(var_name=var, value=line[var])

                            else:
                                tvs.update_variable_value(var_name=var, value="")
                                logger.debug("Cannot find value for variable %s for TVS "
                                             "object %s using CSV line %s" % (var, repr(tvs), line))
            else:
                # hostname not defined, no creation possible
                flash("No hostname in CSV line found: %s" % line, "warning")
            counter += 1

        return redirect(url_for("view_config_template", project_id=project_id, config_template_id=config_template_id))

    else:
        form.csv_content.data = ";".join(variable_list)
        for tvs in config_template.template_value_sets.all():
            values = []
            for var in variable_list:
                values.append(tvs.get_template_value_by_name_as_string(var))
            form.csv_content.data += "\n" + ";".join(values)

    return render_template(
        "config_template/edit_all_config_template_values.html",
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

        except Exception:
            msg = "Config Template <strong>%s</strong> was not deleted (unknown error, see log for details)" % config_template.name
            flash(msg, "error")
            logger.error(msg, exc_info=True)
            db.session.rollback()

        flash("Config Template %s successful deleted" % config_template.name, "success")
        return redirect(url_for("view_project", project_id=project_id))

    return render_template(
        "config_template/delete_config_template.html",
        project_id=project_id,
        config_template=config_template
    )


@app.route(ROOT_URL + "project/<int:project_id>/template/<int:config_template_id>/export")
def export_configurations(project_id, config_template_id):
    """
    Export the configuration to various locations
    :param project_id:
    :param config_template_id:
    :return:
    """
    project = Project.query.filter(Project.id == project_id).first_or_404()
    config_template = ConfigTemplate.query.filter(ConfigTemplate.id == config_template_id).first_or_404()

    return render_template(
        "config_template/export_configurations.html",
        project_id=project_id,
        project=project,
        config_template=config_template,
        ftp_password=get_appliance_ftp_password(),
        ip_addresses=get_local_ip_addresses(),
        appliance_status=verify_appliance_status()
    )