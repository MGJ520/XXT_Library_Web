from config import LOW_MAX_REQUESTS, LOW_REQUEST_TIME_WINDOW
from . import admin

from flask import request, redirect, url_for, render_template, send_from_directory
from utils.Jwt_Function import verify_jwt
from .. import rate_limit_ip


@admin.route('/server-log', methods=['GET'])
@rate_limit_ip('/server-log', LOW_MAX_REQUESTS, LOW_REQUEST_TIME_WINDOW)
def service_management_page():
    """
    主页路由。
    如果用户已登录（即请求头中包含有效的JWT），渲染主页模板。
    否则，重定向到登录页面。
    """
    token = request.cookies.get('auth_token')  # 从Cookie中获取JWT
    if token:
        user_email = verify_jwt(token)  # 验证JWT
        if user_email:
            return render_template('server log.html')  # 验证成功，渲染主页模板
    return redirect(url_for('user.login'))