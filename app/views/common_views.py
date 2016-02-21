"""
common views for the web service
"""
import os

from flask import redirect, render_template, jsonify, request, url_for
from app import app
from app.utils.appliance import verify_appliance_status, get_local_ip_addresses
from app.utils.export import get_appliance_ftp_password
from config import ROOT_URL


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


@app.route(ROOT_URL + "shell")
def shell():
    """embedded shell in a box view

    :return:
    """
    return render_template("shell.html")


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


@app.route(ROOT_URL + "appliance")
def appliance_status():
    """Appliance Status page (services and dependencies), provides test capability for the celery task queue

    :return:
    """
    return render_template(
        "appliance_status.html",
        ftp_password=get_appliance_ftp_password(),
        ip_addresses=get_local_ip_addresses()
    )


@app.route(ROOT_URL + "appliance/service_status")
def appliance_status_json():
    """
    Appliance Status JSON call
    :return:
    """
    return jsonify(verify_appliance_status())


@app.route(ROOT_URL + "debug/list_ftp_directory")
def list_ftp_directory():
    """
    debug view to create a tree structure of the FTP directory
    :return:
    """
    directoy_list_html = ""

    for root, dirs, files in os.walk(app.config["FTP_DIRECTORY"]):
        directoy_list_html += "<p>%s</p>\n<ul>\n" % root[len(app.config["FTP_DIRECTORY"]):]
        for file in files:
            directoy_list_html += "<li>%s</li>\n" % file
        directoy_list_html += "</ul>\n"

    return "<html><body>%s</body></html>" % directoy_list_html


@app.route(ROOT_URL + "debug/list_tftp_directory")
def list_tftp_directory():
    """
    debug view to create a tree structure of the TFTP directory
    :return:
    """
    directoy_list_html = ""

    for root, dirs, files in os.walk(app.config["TFTP_DIRECTORY"]):
        directoy_list_html += "<p>%s</p>\n<ul>\n" % root[len(app.config["TFTP_DIRECTORY"]):]
        for file in files:
            directoy_list_html += "<li>%s</li>\n" % file
        directoy_list_html += "</ul>\n"

    return "<html><body>%s</body></html>" % directoy_list_html
