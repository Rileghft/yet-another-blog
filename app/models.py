# -*- coding: utf-8 -*-

from flask import current_app
from app import db, login_manager
from app.config import config
from sqlalchemy import Column, CHAR, String, Boolean, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
from flask_login import UserMixin, AnonymousUserMixin
from datetime import datetime
import bcrypt
import hmac
from itsdangerous import TimedSerializer, BadTimeSignature
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
