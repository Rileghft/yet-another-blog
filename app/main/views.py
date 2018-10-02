# -*- coding: utf-8 -*-

from . import main
from flask import render_template, current_app, flash, abort, request
from flask_login import current_user, login_required
from sqlalchemy_searchable import search
from app.models import Post, User
from app.config import config


@main.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    search_keywords = request.args.get('search', '').strip()
    query = Post.query.join(Post.author).order_by(Post.created_on.desc())
    if search_keywords:
        query = search(query, search_keywords.replace(' ', ' or '))
    pagination = query.paginate(page, per_page=config['POSTS_PER_PAGE'], error_out=False)
    posts = pagination.items
    return render_template('main/index.html', posts=posts, pagination=pagination, search_keywords=search_keywords)


@main.route('/@<username>/')
def user_page(username):
    user = User.query.filter_by(username=username).first()
    if not user:
        abort(404)
    page = request.args.get('page', 1, type=int)
    search_keywords = request.args.get('search', '').strip()
    query = Post.query.filter_by(author_uuid=user.user_uuid).order_by(Post.created_on.desc())
    if search_keywords:
        query = search(query, search_keywords.replace(' ', ' or '))
    pagination = query.paginate(page, per_page=config['POSTS_PER_PAGE'], error_out=False)
    posts = pagination.items
    return render_template('main/user.html', visit_user=user, posts=posts, pagination=pagination, search_keywords=search_keywords)


@main.route('/@<username>/<post_uri>')
def post(username, post_uri):
    post = Post.query.filter_by(post_uri=post_uri).first()
    author_uuid = post.author_uuid if post else None
    return render_template('main/post.html', author=author_uuid)


@main.route('/new-post')
@login_required
def new_post():
    return render_template('main/new_post.html')


@main.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404
