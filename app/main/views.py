# -*- coding: utf-8 -*-

from . import main
from flask import render_template, current_app
from flask_login import current_user


@main.route('/')
def index():
    return render_template('main/index.html', user=current_user)


@main.errorhandler(404)
def not_found(e):
    return main.send_static_file('404.html'), 404
