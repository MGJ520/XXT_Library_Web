# app/__init__.py
from functools import wraps

from flask import Flask, send_from_directory, request

from functools import wraps
from collections import defaultdict, deque
from datetime import datetime, timedelta
from flask import request, jsonify

# 初始化服务请求计数器
service_request_counts = defaultdict(lambda: defaultdict(lambda: deque(maxlen=1000)))
import os

def rate_limit_ip(service_name, max_requests, time_window):
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            client_ip = request.remote_addr
            current_time = datetime.now()
            timestamps = service_request_counts[service_name][client_ip]

            # 清理过期的请求记录
            while timestamps and current_time - timestamps[0] > time_window:
                timestamps.popleft()

            # 检查当前IP的请求次数
            if len(timestamps) >= max_requests:
                return jsonify({"error": "Please slow down, < (￣︶￣)>"}), 429

            # 添加当前请求的时间戳
            timestamps.append(current_time)

            return f(*args, **kwargs)

        return wrapped

    return decorator



def create_app():
    app = Flask(__name__)

    # app.config.from_object('config.DevelopmentConfig')  # 加载配置


    # 注册蓝本
    # from app.errors import errors as errors_blueprint
    # app.register_blueprint(errors_blueprint)

    # 自定义静态文件路径
    @app.route('/<path:filename>')
    def custom_static(filename):
        return send_from_directory(os.path.join(app.root_path, 'static'), filename)

    from app.user import user as user_blueprint
    app.register_blueprint(user_blueprint)

    from app.index import index as index_blueprint
    app.register_blueprint(index_blueprint)


    from app.admin import admin as admin_blueprint
    app.register_blueprint(admin_blueprint)


    return app