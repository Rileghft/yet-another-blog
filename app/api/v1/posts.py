# -*- coding: utf-8 -*-

from app import db
from app.config import config
from flask import Blueprint, request, jsonify, current_app, url_for
from flask_login import login_required, current_user
from app.models import Post, User
from app.api import api
from datetime import datetime
from hashlib import sha256
from urllib.parse import quote
import html
import json


@api.route('/posts/<post_uri>', methods=['GET'])
def get_post(post_uri):
    post = Post.query.filter_by(post_uri=post_uri).first()
    if post:
        return jsonify(post.to_json())
    return jsonify({}), 404


@api.route('/posts/', methods=['POST'])
@login_required
def new_post():
    data = request.get_json()
    new_post = Post.from_json(data, current_user.user_uuid)
    if new_post:
        db.session.add(new_post)
        db.session.commit()
        return jsonify({'success': True, 'post_uri': '@' + current_user.username + '/' + new_post.post_uri}), 200
    return jsonify({'success': False}), 400


@api.route('/posts/<post_uri>', methods=['PATCH'])
@login_required
def edit_post(post_uri):
    data = request.get_json()
    post = Post.query.filter_by(post_uri=post_uri).first()
    if not post.author_uuid == current_user.user_uuid:
        return jsonify({'success': False}), 401
    if post:
        post.body = html.escape(json.dumps(data.get('body', '')), quote=False)
        post.body_text = html.escape(data.get('body_text', ''), quote=False)
        if post.title != data.get('title'):
            post.title = html.escape(data.get('title', ''))
            hash_postfix = sha256(post.post_uri.encode('utf-8')).hexdigest()[:20]
            post.post_uri = quote(post.title.replace(' ', '-') + '-' + hash_postfix)
        post.updated_on = datetime.utcnow()
        db.session.add(post)
        db.session.commit()
        return jsonify({'success': True, 'post_uri': post.post_uri}), 200
    else:
        return jsonify({'success': False}), 404
    return jsonify({'success': False}), 400


@api.route('/posts/<post_uri>', methods=['DELETE'])
@login_required
def delete_post(post_uri):
    post = Post.query.filter_by(post_uri=post_uri).first()
    if current_user.user_uuid == post.author_uuid:
        db.session.delete(post)
        db.session.commit()
        return jsonify({'success': True}), 200
    elif not post:
        return jsonify({'success': False, 'msg': 'post not found'}), 404
    return jsonify({'success': False}), 400
