# -*- coding: utf-8 -*-

from flask import Blueprint
from flask_login import current_user

auth = Blueprint('auth', __name__)


@auth.app_context_processor
def inject_user():
    return dict(user=current_user)


from . import views
