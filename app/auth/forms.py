# -*- coding: utf-8 -*-

from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, PasswordField
from wtforms.validators import InputRequired, Email, EqualTo, Length


class LoginForm(FlaskForm):
    email = StringField('email', validators=[InputRequired(), Email()])
    password = PasswordField('password', validators=[InputRequired()])
    remember_me = BooleanField('Keep me logged in')


class RegisterForm(FlaskForm):
    username = StringField('username', validators=[InputRequired(), Length(3, 100)])
    email = StringField('email', validators=[InputRequired(), Email(message='Invalid email format')])
    password = PasswordField('password', validators=[InputRequired(), EqualTo('confirm_password', message='password doesn\'t match confirm password')])
    confirm_password = PasswordField('confirm password', validators=[InputRequired()])


class EmailChangeForm(FlaskForm):
    email = StringField('email', validators=[InputRequired(), Email(message='Invalid email format')])


class PasswordChangeForm(FlaskForm):
    old_password = PasswordField('old_password', validators=[InputRequired()])
    new_password = PasswordField('new_password', validators=[InputRequired(), EqualTo('confirm_password', message='password doesn\'t match confirm password')])
    confirm_password = PasswordField('confirm password', validators=[InputRequired()])