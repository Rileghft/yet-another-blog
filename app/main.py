# -*- coding: utf-8 -*-

import os
import argparse
from app import config
from flask import Flask, render_template
from flask_cors import CORS

app = Flask(__name__, template_folder='templates')
CORS(app)


def setup_app(app):
    config_path = os.environ['CONFIG_PATH']
    config.init({'config_path': config_path})

setup_app(app)


@app.route('/')
def main_page():
    return render_template('main.html')


@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run(debug=True)
