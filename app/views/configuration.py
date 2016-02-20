"""
views for the resulting configuration
"""
import logging
import zipfile
from io import BytesIO
import time
from flask import render_template, make_response, send_file
from app import app
from app.models import ConfigTemplate, TemplateValueSet, Project
from app.utils.appliance import get_local_ip_addresses
from app.utils.export import get_appliance_ftp_password
from config import ROOT_URL

logger = logging.getLogger()


@app.route(ROOT_URL + "project/template/<int:config_template_id>/valueset/<int:template_value_set_id>/config")
def view_config(config_template_id, template_value_set_id):
    """view the resulting configuration

    :param config_template_id:
    :param template_value_set_id:
    :return:
    """
    config_template = ConfigTemplate.query.filter(ConfigTemplate.id == config_template_id).first_or_404()
    template_value_set = TemplateValueSet.query.filter(TemplateValueSet.id == template_value_set_id).first_or_404()

    # generate configuration
    config_result = template_value_set.get_configuration_result()

    return render_template(
        "configuration/view_configuration.html",
        config_template=config_template,
        template_value_set=template_value_set,
        ftp_password=get_appliance_ftp_password(),
        ip_addresses=get_local_ip_addresses(),
        project=config_template.project,
        config_result=config_result
    )


@app.route(ROOT_URL + "project/template/<int:config_template_id>/valueset/<int:template_value_set_id>/config_download")
def download_config(config_template_id, template_value_set_id):
    """download the resulting configuration

    :param config_template_id:
    :param template_value_set_id:
    :return:
    """
    ConfigTemplate.query.filter(ConfigTemplate.id == config_template_id).first_or_404()
    template_value_set = TemplateValueSet.query.filter(TemplateValueSet.id == template_value_set_id).first_or_404()

    # generate configuration
    config_result = template_value_set.get_configuration_result()

    response = make_response(config_result)
    response.headers["Content-Disposition"] = "attachment; filename=%s_config.txt" % template_value_set.hostname
    return response


@app.route(ROOT_URL + "project/<int:project_id>/template/<int:config_template_id>/download_configs")
def download_all_config_as_zip(project_id, config_template_id):
    """generate all configuration files and download them as a ZIP archive

    :param project_id:
    :param config_template_id:
    :return:
    """
    Project.query.filter(Project.id == project_id).first_or_404()
    config_template = ConfigTemplate.query.filter(ConfigTemplate.id == config_template_id).first_or_404()

    # generate ZIP archive with all configurations
    memory_file = BytesIO()
    with zipfile.ZipFile(memory_file, 'w') as zf:
        for values in config_template.template_value_sets.all():
            data = zipfile.ZipInfo(values.hostname + "_config.txt")
            data.date_time = time.localtime(time.time())[:6]
            data.compress_type = zipfile.ZIP_DEFLATED
            zf.writestr(data, values.get_configuration_result())
    memory_file.seek(0)

    return send_file(memory_file, attachment_filename=config_template.name + "_configs.zip", as_attachment=True)