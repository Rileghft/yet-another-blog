# -*- coding: utf-8 -*-

from flask import render_template, current_app
from flask_mail import Message
from . import mail
from threading import Thread


def send_email_async(app, msg):
    with app.app_context():
        mail.send(msg)


def send_email(recipients, subject, template, **kwargs):
    app = current_app._get_current_object()
    msg = Message(subject='%s %s' % (app.config['MAIL_PREFIX'], subject), recipients=recipients)
    msg.body = render_template('%s.txt' % template, **kwargs)
    msg.html = render_template('%s.html' % template, **kwargs)
    thread = Thread(target=send_email_async, args=[app, msg])
    thread.start()
    return thread
