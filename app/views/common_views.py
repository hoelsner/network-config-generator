"""
common views for the web service
"""
from flask import redirect, render_template, jsonify, request, url_for
from app import app
from app.utils.appliance import verify_appliance_status, get_local_ip_addresses
from config import ROOT_URL
from app.tasks import debug_celery_task


@app.route("/")
def redirect_to_homepage():
    """static redirect to the homepage

    :return:
    """
    return redirect(ROOT_URL)


@app.route(ROOT_URL)
def home():
    """homepage for the web service

    :return:
    """
    return render_template("home.html")


@app.route(ROOT_URL + "how_to_use")
def how_to_use():
    """How to use page

    :return:
    """
    return render_template("how_to_use.html")


@app.route(ROOT_URL + "template_syntax")
def template_syntax():
    """Templating 101 page

    :return:
    """
    return render_template("template_syntax.html")


@app.route(ROOT_URL + "appliance", methods=['GET', 'POST'])
def appliance_status():
    """Appliance Status page (services and dependencies), provides test capability for the celery task queue

    :return:
    """
    return render_template(
        "appliance_status.html",
        ip_addresses=get_local_ip_addresses()
    )


@app.route(ROOT_URL + "appliance/service_status")
def appliance_status_json():
    """
    Appliance Status JSON call
    :return:
    """
    return jsonify(verify_appliance_status())


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
