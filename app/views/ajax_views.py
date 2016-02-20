from flask import request, jsonify, url_for

from app import app
from config import ROOT_URL
from app.tasks import debug_celery_task
from app.tasks import update_local_ftp_configurations, update_local_tftp_configurations


@app.route(ROOT_URL + "debug/calculate_task", methods=['POST'])
def debug_calculate_task():
    """
    Ajax view that create a simple calculation job
    :return:
    """
    a = request.form.get('a', type=int)
    b = request.form.get('b', type=int)

    task = debug_celery_task.delay(a, b)

    return jsonify({}), 202, {'Location': url_for('task_status_json', task_id=task.id)}


@app.route(ROOT_URL + "export/template/<int:config_template_id>/local_ftp", methods=['POST'])
def update_local_ftp_config_task(config_template_id):
    """
    used to trigger the update of the local FTP files for the given config template
    :param config_template_id:
    :return:
    """
    task = update_local_ftp_configurations.delay(config_template_id)

    return jsonify({}), 202, {'Location': url_for('task_status_json', task_id=task.id)}


@app.route(ROOT_URL + "export/template/<int:config_template_id>/local_tftp", methods=['POST'])
def update_local_tftp_config_task(config_template_id):
    """
    used to trigger the update of the local TFTP files for the given config template
    :param config_template_id:
    :return:
    """
    task = update_local_tftp_configurations.delay(config_template_id)

    return jsonify({}), 202, {'Location': url_for('task_status_json', task_id=task.id)}
