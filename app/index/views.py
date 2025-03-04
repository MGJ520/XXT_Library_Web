import os

from flask import request, redirect, url_for, render_template, send_from_directory

from config import LOW_MAX_REQUESTS, LOW_REQUEST_TIME_WINDOW
from utils.Jwt_Function import verify_jwt
from . import index
from .. import rate_limit_ip


@index.route('/', methods=['GET', 'POST'])
@rate_limit_ip('/', LOW_MAX_REQUESTS, LOW_REQUEST_TIME_WINDOW)
def root():
    """
    根页面路由。
    """
    token = request.cookies.get('auth_token')  # 从Cookie中获取JWT
    if token:
        user_email = verify_jwt(token)  # 验证JWT
        if user_email:
            return redirect(url_for('index.index_page'))  # 验证成功，渲染主页模板
    return redirect(url_for('user.login'))


@index.route('/index', methods=['GET'])
@rate_limit_ip('/index', LOW_MAX_REQUESTS, LOW_REQUEST_TIME_WINDOW)
def index_page():
    """
    主页路由。
    如果用户已登录（即请求头中包含有效的JWT），渲染主页模板。
    否则，重定向到登录页面。
    """
    token = request.cookies.get('auth_token')  # 从Cookie中获取JWT
    if token:
        user_email = verify_jwt(token)  # 验证JWT
        if user_email:
            return render_template('index.html')  # 验证成功，渲染主页模板
    return redirect(url_for('user.login'))


# 帮助
@index.route('/help', methods=['GET'])
@rate_limit_ip('/help', LOW_MAX_REQUESTS, LOW_REQUEST_TIME_WINDOW)
def help_page():
    """
    主页路由。
    如果用户已登录（即请求头中包含有效的JWT），渲染主页模板。
    否则，重定向到登录页面。
    """
    token = request.cookies.get('auth_token')  # 从Cookie中获取JWT
    if token:
        user_email = verify_jwt(token)  # 验证JWT
        if user_email:
            return render_template('help.html')  # 验证成功，渲染主页模板
    return redirect(url_for('user.login'))