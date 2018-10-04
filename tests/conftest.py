# -*- coding: utf-8 -*-

from pytest import fixture
from app import app as default_app, create_app


@fixture
def app():
    default_app = create_app()
    return default_app
