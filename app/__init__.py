# -*- coding: utf-8 -*-

import os
from app import config
from flask import Flask
from flask_cors import CORS
from flask_wtf import CSRFProtect
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_searchable import make_searchable
from flask_migrate import Migrate
from flask_mail import Mail

app = None
login_manager = LoginManager()
db = SQLAlchemy()
migrate = Migrate()
mail = Mail()


def create_app():
    app = Flask(__name__, template_folder='templates')
    CORS(app)
    CSRFProtect(app)
    config.init(os.environ['CONFIG_PATH'])
    app.config['SECRET_KEY'] = config.config['secret_key']
    app.config['SQLALCHEMY_DATABASE_URI'] = config.config['db_url']
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ECHO'] = app.debug
    app.config.update(**config.config['mail'])
    app.config['MAIL_USERNAME'] = os.environ['APP_MAIL_USERNAME']
    app.config['MAIL_PASSWORD'] = os.environ['APP_MAIL_PASSWORD']
    login_manager.init_app(app)
    db.init_app(app)
    make_searchable(db.metadata)
    db.create_all(app=app)
    mail.init_app(app)
    migrate.init_app(app, db)
    from .auth import auth
    app.register_blueprint(auth, url_prefix='/auth')
    from .main import main
    app.register_blueprint(main, url_prefix='/')
    from .api import api
    app.register_blueprint(api, url_prefix='/api')

    return app
