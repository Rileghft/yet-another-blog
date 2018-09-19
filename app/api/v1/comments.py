# -*- coding: UTF-8 -*-

from flask import request, abort, jsonify, current_app
from flask_login import current_user
from app.api import api
from app.models import Post, Comment
from app import db


@api.route('/comments', methods=['GET'])
def get_comments():
    post_uri = request.args.get('post_uri')
    post = Post.query.filter_by(post_uri=post_uri).first()
    if not post:
        abort(404)
    return jsonify({'comments': [comment.to_json() for comment in post.comments.all()]})


@api.route('/comments', methods=['POST'])
def new_comment():
    post_uri = request.args.get('post_uri')
    post = Post.query.filter_by(post_uri=post_uri).first()
    if not post:
        return jsonify({'success': False}), 404
    data = request.get_json()
    new_comment = Comment.from_json(data, post, current_user)
    db.session.add(new_comment)
    db.session.commit()
    return jsonify({'success': True}), 200
