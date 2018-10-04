# -*- coding: utf-8 -*-

import uuid
from app import create_app
from app import config
import app as app_module
from pytest import fixture
import datetime
import arrow


@fixture
def default_user(app):
    user = app_module.models.User(user_uuid=uuid.uuid4(), email='email@example.com', username='test')
    return user


def test_password_setter(default_user):
    password = 'password'
    default_user.password = password
    assert default_user.verify_password(password)


def test_password_verification(default_user):
    password = 'password'
    default_user.password = password
    assert default_user.verify_password(password)
    assert not default_user.verify_password('invalid')


def test_password_salt_random(default_user):
    password = 'password'
    default_user.password = password
    user = app_module.models.User(password=password)
    assert default_user.password_hash != user.password_hash


def test_confirmation_token(app, default_user, mocker):
    with app.app_context():
        mocker.patch('app.db.session.commit')
        token = default_user.generate_confirmation_token()
        assert default_user.confirm(token)
        # test token expired
        token = default_user.generate_confirmation_token(expiration=-700)
        assert not default_user.confirm(token)


def test_email_confirmation_token(app, default_user, mocker):
    with app.app_context():
        mocker.patch('app.db.session.commit')
        new_email = 'email2@example.com'
        token = default_user.generate_email_confirmation_token(new_email)
        assert default_user.confirm_email_change(token)
        # test token expired
        token = default_user.generate_email_confirmation_token(new_email, expiration=-700)
        assert not default_user.confirm_email_change(token)
