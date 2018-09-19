# -*- coding: utf-8 -*-

from flask import current_app
from app import db, login_manager
from app.config import config
from sqlalchemy import Column, CHAR, String, Text, Boolean, TIMESTAMP, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from flask_login import UserMixin, AnonymousUserMixin
from datetime import datetime
import bcrypt
import hmac
import uuid
from itsdangerous import TimedSerializer, BadTimeSignature
import arrow
import json
from hashlib import sha256
from urllib.parse import quote
import html
import arrow


@login_manager.user_loader
def load_user(user_uuid):
    return User.query.filter_by(user_uuid=user_uuid).first()


class User(UserMixin, db.Model):
    __tablename__ = 'user'

    user_uuid = Column(UUID(as_uuid=True), primary_key=True)
    email = Column(String(254), unique=True, nullable=False)
    username = Column(String(100), nullable=False)
    password_hash = Column(CHAR(length=128), nullable=False)
    salt = Column(CHAR(length=29))
    confirmed = Column(Boolean, default=False)
    confirmed_on = Column(TIMESTAMP)
    suspend = Column(Boolean, default=False)
    register_on = Column(TIMESTAMP, default=datetime.utcnow)
    last_login = Column(TIMESTAMP)
    last_modified = Column(TIMESTAMP, default=datetime.utcnow)

    def get_id(self):
        return self.user_uuid

    @property
    def password(self):
        raise AttributeError('password a is readonly attribute')

    @password.setter
    def password(self, password):
        salt = bcrypt.gensalt(rounds=config['security']['hash_round'])
        self.salt = salt.decode('utf-8')
        hash_password = bcrypt.hashpw(password.encode('utf-8'), salt)
        self.password_hash = hmac.HMAC(config['secret_key'].encode('utf-8'), msg=hash_password, digestmod=config['security']['digestmod']).hexdigest()

    def verify_password(self, password):
        hash_password = bcrypt.hashpw(password.encode('utf-8'), self.salt.encode('utf-8'))
        password_to_verify = hmac.HMAC(config['secret_key'].encode('utf-8'), msg=hash_password, digestmod=config['security']['digestmod']).hexdigest()
        return hmac.compare_digest(password_to_verify, self.password_hash)

    def is_active(self):
        return not self.is_suspend

    def generate_confirmation_token(self, expiration=600):
        serializer = TimedSerializer(config['secret_key'])
        return serializer.dumps({
            'confirm_register': self.user_uuid.hex,
            'expired_on': arrow.utcnow().timestamp + expiration
            })

    def confirm(self, token):
        serializer = TimedSerializer(config['secret_key'])
        try:
            msg = serializer.loads(token)
            now = arrow.utcnow().timestamp
            current_app.logger.info(msg)
            if msg.get('confirm_register') == self.user_uuid.hex \
                    and msg.get('expired_on', now) > now:
                self.confirmed = True
                self.confirmed_on = datetime.utcnow()
                db.session.add(self)
                db.session.commit()
                current_app.logger.info('User %s: confirmed', self.user_uuid.hex)
                return True
        except BadTimeSignature:
            current_app.logger.error('User %s: failed to confirm', self.user_uuid.hex)
        return False


class AnonymousUser(AnonymousUserMixin):
    confirmed = False


login_manager.anonymous_user = AnonymousUser


class Post(db.Model):
    __tablename__ = 'post'

    post_uuid = Column(UUID(as_uuid=True), primary_key=True)
    post_uri = Column(String(120), unique=True, nullable=False)
    author_uuid = Column(UUID(as_uuid=True), ForeignKey('user.user_uuid'), nullable=False)
    author = relationship('User', lazy='joined')
    title = Column(String(100), nullable=False)
    body = Column(Text)
    body_text = Column(Text)
    created_on = Column(TIMESTAMP, default=datetime.utcnow)
    updated_on = Column(TIMESTAMP, default=datetime.utcnow)
    comments = relationship('Comment', backref='post', cascade='delete', lazy='dynamic')


    def to_json(self):
        return {
            'title': self.title,
            'body': json.loads(self.body),
            'body_text': self.body_text,
            'created_on': arrow.get(self.created_on).timestamp,
            'updated_on': arrow.get(self.updated_on).timestamp
        }

    @staticmethod
    def from_json(data, author_uuid):
        if 'title' not in data or 'body' not in data\
                or not data['title'] or not data['body']:
            return None
        now = str(datetime.utcnow())
        postfix = data['title'] + author_uuid.hex + now
        hash_postfix = sha256(postfix.encode('utf-8')).hexdigest()[:20]
        post_uri = quote(data['title'].replace(' ', '-') + '-' + hash_postfix)
        post = Post(
            post_uuid=uuid.uuid4().hex,
            author_uuid=author_uuid,
            post_uri=post_uri,
            title=html.escape(data['title']),
            body=html.escape(json.dumps(data['body']), quote=False),
            body_text=html.escape(data['body_text'], quote=False)
        )
        return post


class Comment(db.Model):
    __tablename__ = 'comment'

    comment_uuid = Column(UUID(as_uuid=True), primary_key=True)
    author_uuid = Column(UUID(as_uuid=True), ForeignKey('user.user_uuid'), nullable=False)
    author = relationship('User', lazy='immediate')
    post_uuid = Column(UUID(as_uuid=True), ForeignKey('post.post_uuid'), index=True, nullable=False)
    content = Column(Text)
    comment_on = Column(TIMESTAMP, default=datetime.utcnow)

    def to_json(self):
        return {
            'author': self.author.username,
            'comment_on': self.comment_on,
            'content': self.content
        }

    @staticmethod
    def from_json(data, post, author):
        return Comment(
            comment_uuid=uuid.uuid4(),
            author_uuid=author.user_uuid,
            post_uuid=post.post_uuid,
            content=html.escape(data['content'], quote=False)
        )