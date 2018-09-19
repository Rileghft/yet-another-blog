# -*- coding: utf-8 -*-

from flask import render_template, redirect, url_for, flash, request, current_app
from flask_login import current_user, login_required, login_user, logout_user
from . import auth
from .forms import LoginForm, RegisterForm
from app import db
from app.models import User
from app.email import send_email
import uuid
import html
from datetime import datetime


@auth.route('unconfirm')
@login_required
def unconfirm():
    return render_template('auth/unconfirm.html')


@auth.route('login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            if not user.confirmed:
                return redirect(url_for('auth.unconfirm'))
            return redirect(request.args.get('next') or url_for('main.index'))
        else:
            flash('Invalid email or password.')
    return render_template('auth/login.html', form=form)


@auth.route('register', methods=['POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if User.query.filter_by(email=form.email.data).first():
            flash('%s already registered.' % (form.email.data))
            flash('If you forgot your password, click forgot password to reset.')
        else:
            try:
                new_user = User(
                    user_uuid=uuid.uuid4().hex,
                    email=form.email.data,
                    username=html.escape(form.username.data),
                    password=form.password.data,
                )
                db.session.add(new_user)
                db.session.commit()
                send_email([new_user.email], 'confirm your account', 'auth/mail/confirm', user=new_user, token=new_user.generate_confirmation_token())
                flash('Please check your email and confirm your account.')
            except Exception as e:
                flash('register failed.')
                current_app.logger.exception(str(e))
    return redirect(url_for('auth.login'))


@auth.route('confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        flash('Your account is already confirmed.')
    elif current_user.confirm(token):
        user = current_user._get_current_object()
        user.confirmed = True
        user.confirmed_on = datetime.utcnow()
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('main.index'))
    else:
        flash('failed to confirm your account, resend confirmation and try again.')
    return redirect(url_for('auth.unconfirm'))


@auth.route('resend_confirmation')
@login_required
def resend_confirmation():
    if not current_user.confirmed:
        send_email([current_user.email], 'confirm your account', 'auth/mail/confirm')
        flash('Please check your email and confirm your account.')
    else:
        flash('Your account is already confirmed.')
    return redirect(url_for('auth.unconfirm'))


@auth.route('logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))
