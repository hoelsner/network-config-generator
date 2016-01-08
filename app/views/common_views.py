"""
common views for the web service
"""
from flask import redirect, render_template
from app import app
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
