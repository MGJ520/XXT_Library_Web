from flask import request, make_response, jsonify

from config import Room_data, HIGN_MAX_REQUESTS, HIGN_REQUEST_TIME_WINDOW, HIGN_LONG_MAX_REQUESTS, \
    HIGN_LONG_REQUEST_TIME_WINDOW, LOW_MAX_REQUESTS, LOW_REQUEST_TIME_WINDOW
from utils.Database_Function import DatabaseManager
from utils.General_Function import get_status_code_by_name, is_email
from utils.Jwt_Function import create_jwt, verify_jwt
from utils.Xxt_WebApi import XxTWebApi
from . import user
from .. import rate_limit_ip


# 登录接口
@user.route('/api/login', methods=['POST'])
@rate_limit_ip('/api/login', HIGN_MAX_REQUESTS, HIGN_REQUEST_TIME_WINDOW)
def api_login():
    """
    登录接口。
    验证用户提供的电子邮件和密码。
    如果验证成功，返回包含JWT的响应。
    如果验证失败，返回错误信息。
    """
    data = request.json
    email_local = data.get('email_login_local')
    password_local = data.get('password_login_local')
    db_manager = DatabaseManager()
    if db_manager.login_user(
            platform_email=email_local,
            platform_password=password_local,
            user_ip=request.remote_addr
    ):
        # 用户验证成功，创建JWT
        token = create_jwt(email_local, email_local)
        response = make_response(jsonify({'success': True}))
        response.set_cookie('auth_token', token, httponly=True, samesite='Lax', path='/')
        return response
    else:
        # 用户验证失败，返回错误信息
        return jsonify({'success': False, 'error': 'Invalid username or password'})


# 注册接口
@user.route('/api/register', methods=['POST'])
@rate_limit_ip('/api/register', HIGN_LONG_MAX_REQUESTS, HIGN_LONG_REQUEST_TIME_WINDOW)
def api_register():
    """
    注册接口。
    注册新用户。
    如果用户已存在，返回错误信息。
    如果注册成功，返回成功信息。
    """
    data = request.json
    print(data)
    username_local = data.get('username_register_local')
    email_local = data.get('email_register_local')
    # print(is_email(email_local))
    # print(email_local)
    password_local = data.get('password_register_local')
    if email_local and username_local and password_local:
        if not is_email(email_local):
            return jsonify({'success': False, 'error': f'{email_local} is not a email'})
        # 注册新用户，存储密码哈希值
        db_manager = DatabaseManager()
        # 注册新用户
        register_result = db_manager.register_user(
            platform_email=email_local,
            platform_nickname=username_local,
            platform_password=password_local,
            user_ip=request.remote_addr
        )
        return register_result

    else:
        # 返回错误信息
        return jsonify({'success': False, 'error': 'Please input data'})


# 注销接口
@user.route('/api/logout', methods=['GET'])
@rate_limit_ip('/api/logout', LOW_MAX_REQUESTS, LOW_REQUEST_TIME_WINDOW)
def api_logout():
    response = make_response(jsonify({'success': True}))
    response.set_cookie('auth_token', '', expires=0)
    return response



@user.route('/api/update/profile', methods=['POST'])
@rate_limit_ip('/api/update/profile', LOW_MAX_REQUESTS, LOW_REQUEST_TIME_WINDOW)
def update_profile():
    token = request.cookies.get('auth_token')  # 从Cookie中获取JWT
    if token:
        user_email = verify_jwt(token)  # 验证JWT
        if user_email:
            data = request.json
            new_nickname = data.get('nickname')
            new_password = data.get('password')
            print(new_nickname, new_password)
            if not new_nickname or not new_password:
                return jsonify({'success': False, 'error': 'Missing data'}), 400
            else:
                db = DatabaseManager()
                if db.update_user_profile(user_email, new_nickname, new_password):
                    return jsonify({'success': True, 'message': 'Profile updated successfully'}), 200
                else:
                    return jsonify({'success': False, 'error': 'Missing data'}), 400
    return jsonify({'success': False, 'error': 'Please login'})


@user.route('/api/get/user_data', methods=['GET'])
@rate_limit_ip('/api/get/user_data', LOW_MAX_REQUESTS, LOW_REQUEST_TIME_WINDOW)
def api_get_user_data():
    token = request.cookies.get('auth_token')  # 从Cookie中获取JWT
    if token:
        user_email = verify_jwt(token)  # 验证JWT
        if user_email:
            db = DatabaseManager()
            user_data = db.fetch_user_information(user_email)
            if user_data is None:
                return jsonify({'error': "User is none"}), 500
            else:
                return jsonify(user_data)
    return jsonify({'success': False, 'error': 'Please login'})


@user.route('/api/get/room_data', methods=['GET'])
@rate_limit_ip('/api/get/room_data', LOW_MAX_REQUESTS, LOW_REQUEST_TIME_WINDOW)
def api_get_room_data():
    token = request.cookies.get('auth_token')  # 从Cookie中获取JWT
    if token:
        user_email = verify_jwt(token)  # 验证JWT
        if user_email:
            return jsonify(Room_data)
    return jsonify({'success': False, 'error': 'Please login'})


@user.route('/api/new_reservation', methods=['POST'])
@rate_limit_ip('/api/new_reservation', LOW_MAX_REQUESTS, LOW_REQUEST_TIME_WINDOW)
def new_reservation():
    token = request.cookies.get('auth_token')  # 从Cookie中获取JWT
    if token:
        user_email = verify_jwt(token)  # 验证JWT
        if user_email:
            db_manager = DatabaseManager()
            # 尝试从JSON请求体中获取数据
            try:
                data = request.json
                # print(data)
            except Exception as e:
                # 如果JSON数据不完整或解析失败，返回错误信息
                return jsonify({'success': False, 'message': f'Invalid JSON data: {str(e)}'}), 400

            # 解析前端发送的数据
            try:
                reservation_account = data.get('reservation_account')
                reservation_password = data.get('reservation_password')
                start_time = data.get('start_time')
                end_time = data.get('end_time')
                room_id = data.get('room_id')
                seat_id = str(data.get('seat_id')).zfill(3)
            except Exception as e:
                return jsonify({'success': False, 'message': f'Missing or invalid field: {str(e)}'}), 400

            # 数据检查
            if not reservation_account:
                return jsonify({'success': False, 'message': 'Reservation account is required'}), 400
            if not reservation_password:
                return jsonify({'success': False, 'message': 'Reservation password is required'}), 400
            if not start_time:
                return jsonify({'success': False, 'message': 'Start time is required'}), 400
            if not end_time:
                return jsonify({'success': False, 'message': 'End time is required'}), 400
            if not room_id:
                return jsonify({'success': False, 'message': 'Room ID is required'}), 400
            if not seat_id:
                return jsonify({'success': False, 'message': 'Seat ID is required'}), 400

            try:

                # 检查预约账号是否已存在
                if db_manager.check_reservation_account_exists(reservation_account):
                    if db_manager.check_email_reservation_account_exists(user_email, reservation_account):
                        # 检查时间是否重叠
                        if db_manager.check_time_overlap(room_id, seat_id, start_time, end_time,
                                                         exclude_reservation_account=reservation_account):
                            return jsonify(
                                {'success': False, 'message': '该座位该时间段已经被占用'}), 400
                        if db_manager.update_reservation(
                                platform_email=user_email,
                                reservation_account=reservation_account,
                                start_time=start_time,
                                end_time=end_time,
                                room_location=room_id,
                                seat_location=seat_id,
                                account_status=9):
                            return jsonify({'success': True, 'message': 'Reservation successful'}), 200
                        else:
                            return jsonify({'success': False, 'error': 'mysql error'})
                    else:
                        return jsonify({'success': False, 'message': 'Reservation account already exists'}), 400

                # 检查时间是否重叠
                if db_manager.check_time_overlap(room_id, seat_id, start_time, end_time):
                    return jsonify(
                        {'success': False, 'message': '该座位该时间段已经被占用'}), 400

                s = XxTWebApi(sleep_time=1, max_attempt=1, reserve_next_day=False)
                s.get_login_status()
                out_login = s.login(reservation_account, reservation_password)

                # 密码错误
                if not out_login[0]:
                    return jsonify(
                        {'success': False, 'message': out_login[1]}), 400

                reservation_end_time = '2025-12-31 17:00:00'
                account_status = 9

                refresh_status = True

                sign_back_status = True

                sign_in_status = False

                reservation_status = False

                monitor_sign_in_status = False

                reservation_times = 10
                sign_in_times = 10
                sign_back_times = 10
                monitor_sign_in_times = 10
                operation_failure_times = 0

                db_manager.insert_reservations(user_email, reservation_account, reservation_password, start_time,
                                               end_time,
                                               reservation_end_time, room_id, seat_id, account_status,
                                               refresh_status,
                                               reservation_status, sign_in_status, sign_back_status,
                                               monitor_sign_in_status,
                                               reservation_times, sign_in_times, sign_back_times, monitor_sign_in_times,
                                               operation_failure_times)
                return jsonify({'success': True, 'message': 'Reservation successful'}), 200

            except Exception as e:
                # 如果在保存预约时发生错误，返回错误信息
                return jsonify({'success': False, 'message': str(e)}), 500
    return jsonify({'success': False, 'error': 'Please login'})


@user.route('/api/get/reservation', methods=['GET'])
@rate_limit_ip('/api/get/reservation', LOW_MAX_REQUESTS, LOW_REQUEST_TIME_WINDOW)
def get_reservation():
    token = request.cookies.get('auth_token')
    if token:
        user_email = verify_jwt(token)
        if user_email:
            db_manager = DatabaseManager()
            data = db_manager.fetch_reservation_information(user_email)
            return jsonify({"success": True, "data": data})
    return jsonify({'success': False, 'error': 'Please login'})


@user.route('/api/delete/reservation', methods=['DELETE'])
@rate_limit_ip('/api/get/reservation', LOW_MAX_REQUESTS, LOW_REQUEST_TIME_WINDOW)
def delete_seat():
    token = request.cookies.get('auth_token')
    if token:
        user_email = verify_jwt(token)
        if user_email:
            db_manager = DatabaseManager()
            # 从请求中获取数据
            data = request.json
            account = data.get('account')

            # 记录日志
            print(f"Attempting to delete appointment for account: {account}")

            # 检查数据库是否存在该账号的预约
            account_exists = db_manager.delete_reservation_account(user_email, account)

            if not account_exists:
                # 如果不存在，返回操作结果
                return jsonify({'success': False, 'message': "没有找到该账号的预约"})
            # 返回操作结果
            return jsonify({'success': True})

    return jsonify({'success': False, 'error': 'Please login'})


@user.route('/api/cancel/reservation_seat', methods=['POST'])
@rate_limit_ip('/api/cancel/reservation_seat', LOW_MAX_REQUESTS, LOW_REQUEST_TIME_WINDOW)
def cancel_seat():
    token = request.cookies.get('auth_token')
    if token:
        user_email = verify_jwt(token)
        if user_email:
            db_manager = DatabaseManager()

            # 从请求中获取数据
            data = request.json
            account = data.get('account')
            appointments = db_manager.fetch_user_email_account_information(user_email, account)

            # 检查appointments是否为空
            if not appointments:
                return jsonify(success=False, message='没有预约数据')

            for item in appointments:
                username, password, times, room_id, seat_id, day_week, is_auto_reservation, account_status = item.values()
                if get_status_code_by_name(account_status) in ['0', '1', '3', '5']:
                    # 登录
                    s = XxTWebApi(sleep_time=1, max_attempt=1, reserve_next_day=False)
                    s.get_login_status()
                    s.login(account, password)
                    s.requests.headers.update({'Host': 'office.chaoxing.com'})
                    if get_status_code_by_name(account_status) in ['0']:
                        suc = s.submit_cancel(account, 'time', room_id, seat_id)
                    else:
                        suc = s.submit_sign_back(account, 'time', room_id, seat_id)
                    # 判断
                    if not suc:
                        return jsonify(success=False, message='退座失败')
                    else:
                        # 如果所有允许退座的预约都成功退座，则返回成功消息
                        db_manager.update_reservations_new_status(account, 2)
                        return jsonify(success=True, message='退座成功')
                else:
                    if not db_manager.check_email_reservation_account_exists(user_email, account):
                        return jsonify(success=False, message='你没有该账户')
                    else:
                        return jsonify(success=False, message='当前不可以退座')

    return jsonify({'success': False, 'error': 'Please login'})


# 查询状态的接口
@user.route("/api/get/server_statuses", methods=["POST"])
@rate_limit_ip('/api/get/server_statuses', LOW_MAX_REQUESTS, LOW_REQUEST_TIME_WINDOW)
def get_statuses_api():
    token = request.cookies.get('auth_token')
    if token:
        user_email = verify_jwt(token)
        if user_email:
            db_manager = DatabaseManager()
            data = request.json
            reservation_account = data.get('reservation_account')
            if not reservation_account:
                return jsonify({"success": False, "message": "缺少必要的参数"}), 400

            status_data = db_manager.get_status_by_email_and_account(user_email, reservation_account)
            if status_data:
                return jsonify({"success": True, "data": status_data})
            else:
                return jsonify({"success": False, "message": "未找到状态数据"}), 404

    return jsonify({'success': False, 'error': 'Please login'})


@user.route("/api/update/server_statuses", methods=["POST"])
@rate_limit_ip('/api/update/server_statuses', LOW_MAX_REQUESTS, LOW_REQUEST_TIME_WINDOW)
def update_statuses_api():
    token = request.cookies.get('auth_token')
    if token:
        user_email = verify_jwt(token)
        if user_email:
            data = request.json
            reservation_account = data.get("reservation_account")
            refresh_status = data.get("refresh_status")
            reservation_status = data.get("reservation_status")
            sign_in_status = data.get("sign_in_status")
            sign_back_status = data.get("sign_back_status")
            # monitor_sign_in_status = data.get("monitor_sign_in_status")
            monitor_sign_in_status = False

            if  not reservation_account:
                return jsonify({"success": False, "message": "缺少必要的参数"}), 400
            db_manager = DatabaseManager()
            # 调用数据库更新方法
            success = db_manager.update_statuses(
                user_email,
                reservation_account,
                refresh_status,
                reservation_status,
                sign_in_status,
                sign_back_status,
                monitor_sign_in_status
            )
            if success:
                return jsonify({"success": True, "message": "状态更新成功"})
            else:
                return jsonify({"success": False, "message": "状态更新失败"}), 500

    return jsonify({'success': False, 'error': 'Please login'})
