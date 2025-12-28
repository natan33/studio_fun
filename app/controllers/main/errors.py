from flask import render_template
from . import main


@main.app_errorhandler(403)
def page_not_found(e):
    return render_template('error/error403.html'), 403


@main.app_errorhandler(404)
def page_not_found(e):
    return render_template('error/error404.html'), 404


@main.app_errorhandler(500)
def page_not_found(e):
    return render_template('error/error500.html'), 500