from flask import render_template
from app import app


@app.errorhandler(404)
def page_not_found(e):
    return render_template('http404.html'), 404


@app.errorhandler(403)
def page_not_found(e):
    return render_template('http403.html'), 403


@app.errorhandler(500)
def page_not_found(e):
    return render_template('http500.html'), 500
