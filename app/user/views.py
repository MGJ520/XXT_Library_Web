# 登录页面
from flask import request, redirect, url_for, render_template

from config import LOW_MAX_REQUESTS, LOW_REQUEST_TIME_WINDOW
from utils.Jwt_Function import verify_jwt

from . import user
from .. import rate_limit_ip


@user.route('/login', methods=['GET', 'POST'])
@rate_limit_ip('/login', LOW_MAX_REQUESTS, LOW_REQUEST_TIME_WINDOW)
def login():
    """
    登录页面路由。
    如果用户已登录（即请求头中包含有效的JWT），重定向到主页。
    否则，渲染登录页面模板。
    """
    token = request.cookies.get('auth_token')  # 从Cookie中获取JWT
    if token:
        user_email = verify_jwt(token)  # 验证JWT
        if user_email:
            return redirect(url_for('index.index_page'))  # 验证成功，重定向到主页
    return render_template("login.html")  # 验证失败，渲染登录页面模板


@user.route('/control-panel', methods=['GET', 'POST'])
@rate_limit_ip('/control-panel', LOW_MAX_REQUESTS, LOW_REQUEST_TIME_WINDOW)
def control_panel():
    """
    主页路由。
    如果用户已登录（即请求头中包含有效的JWT），渲染主页模板。
    否则，重定向到登录页面。
    """
    token = request.cookies.get('auth_token')  # 从Cookie中获取JWT
    if token:
        user_email = verify_jwt(token)  # 验证JWT
        if user_email:
            return render_template('panel.html')  # 验证成功，渲染主页模板
    return redirect(url_for('user.login'))


# 帮助
@user.route('/accounts', methods=['GET', 'POST'])
@rate_limit_ip('/accounts', LOW_MAX_REQUESTS, LOW_REQUEST_TIME_WINDOW)
def accounts_page():
    """
    主页路由。
    如果用户已登录（即请求头中包含有效的JWT），渲染主页模板。
    否则，重定向到登录页面。
    """
    token = request.cookies.get('auth_token')  # 从Cookie中获取JWT
    if token:
        user_email = verify_jwt(token)  # 验证JWT
        if user_email:
            return render_template('accounts.html')  # 验证成功，渲染主页模板
    return redirect(url_for('user.login'))

