import logging
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

from config import TIME_Check_TIME, TIME_MAX_ATTEMPT, TIME_SLEEP_TIME, TIME_START_TIME, TIME_END_TIME
from utils.Database_Function import DatabaseManager
from utils.Xxt_WebApi import XxTWebApi
from utils.General_Function import is_tomorrow, get_current_hour, \
    is_within_m_minutes, is_within_m_minutes_num, parse_time, is_within_time_range, is_today


class ReservationCheckService:
    def __init__(self):
        self.TIME_SLEEP_TIME = TIME_SLEEP_TIME
        self.TIME_MAX_ATTEMPT = TIME_MAX_ATTEMPT
        self.TIME_RESERVE_NEXT_DAY = True
        self.TIME_Check_TIME = TIME_Check_TIME
        self.task_map = {}
        # 配置日志的基本设置，设置日志级别为INFO，并定义日志的格式
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        # 设置为守护线程，这样主线程结束时子线程也会结束
        thread_rs = threading.Thread(target=self.location_serve_main)
        thread_rs.daemon = True
        # 启动学习通座位检查线程
        thread_rs.start()

    def perform_action(self, user, action):
        logging.info(
            f"[Try_{action}] - {user['reservation_account']} -- {user['start_time']}-{user['end_time']}-- {user['room_location']} -- {user['seat_location']} ---- ")
        s = XxTWebApi(sleep_time=self.TIME_SLEEP_TIME, max_attempt=self.TIME_MAX_ATTEMPT,
                      reserve_next_day=self.TIME_RESERVE_NEXT_DAY)
        s.get_login_status()
        s.login(user['reservation_account'], user['reservation_password'])
        s.requests.headers.update({'Host': 'office.chaoxing.com'})

        if action == "sign":
            suc = s.submit_sign(user['reservation_account'], f"{user['start_time']}-{user['end_time']}",
                                user['room_location'], user['seat_location'])
        elif action == "sign_back":
            suc = s.submit_sign_back(user['reservation_account'], f"{user['start_time']}-{user['end_time']}",
                                     user['room_location'], user['seat_location'])
        else:
            raise ValueError("Invalid action specified. Use 'sign' or 'sign_back'.")
        return suc

    def sign(self, user):
        return self.perform_action(user, "sign")

    def sign_back(self, user):
        return self.perform_action(user, "sign_back")


    def check(self, reservation):
        db = DatabaseManager()
        # 访问第一个字典
        user = db.fetch_check_more_information(reservation[0])[0]  # 获取列表中的第一个字典
        # user['reservation_account']
        # user['reservation_password']
        # user['start_time']
        # user['end_time']
        # user['room_location']
        # user['seat_location']
        # user['refresh_status']
        # user['reservation_status']
        # user['sign_in_status']
        # user['sign_back_status']
        # user['monitor_sign_in_status']

        # 尝试预约
        # logging.info(f" ---- [Try_Check] - {username}  ---- ")
        s = XxTWebApi(sleep_time=self.TIME_SLEEP_TIME, max_attempt=self.TIME_MAX_ATTEMPT,
                      reserve_next_day=self.TIME_RESERVE_NEXT_DAY)
        s.get_login_status()
        out_login = s.login(user['reservation_account'], user['reservation_password'])
        # 密码错误
        if not out_login[0]:
            db.update_reservations_new_status(user['reservation_account'], 8)
            return False

        s.requests.headers.update({'Host': 'office.chaoxing.com'})
        # 获取第一个信息
        Seat_info = s.get_seat_reservation_info(user['reservation_account'])
        # 同步到数据库
        db.update_reservations_new_status(user['reservation_account'], Seat_info['status'])

        # 违约
        if Seat_info['type'] == 0:
            db.update_reservations_new_status(user['reservation_account'], 2)
            if is_today(Seat_info['today']):
                logging.error(f"[Find]---------------------------呜呜呜呜呜,违约了------------------------------")
                # 更新数据库，-1表示违约了
                db.update_reservations_new_status(user['reservation_account'], -1)
            return

        # print(datetime.fromtimestamp( Seat_info['expireTime']/ 1000.0))


        # '0': '待履约',
        if Seat_info['status'] == 0:
            # 判断是否为今天
            if not is_tomorrow(Seat_info['startTime']):
                # 如果在20min内
                if is_within_m_minutes(int(time.time() * 1000),Seat_info['expireTime'], 20):
                    logging.info(f"发现预约：{user['reservation_account']}")
                    # 马上签到
                    if not user['sign_in_status']:
                        logging.info(f"权限取消操作：{user['reservation_account']}")
                        return
                    if self.sign(user):
                        db.update_reservations_new_status(user['reservation_account'], 1)

        # '1': '学习中', 少于15分钟，自动退签
        if Seat_info['status'] == 1:
            # 如果在15min内
            if is_within_m_minutes(int(time.time() * 1000), Seat_info['endTime'], 15):
                # 签到
                logging.info(f"发现退签：{user['reservation_account']}")
                if not user['sign_back_status']:
                    logging.info(f"权限取消操作：{user['reservation_account']}")
                    return
                if self.sign_back(user):
                    db.update_reservations_new_status(user['reservation_account'], 2)

        # '5': '被监督中', 自动签到
        if Seat_info['status'] == 5:
            # 签到
            logging.info(f"发现监督：{user['reservation_account']}")
            if not user['monitor_sign_in_status']:
                logging.info(f"权限取消操作：{user['reservation_account']}")
                return
            if self.sign(user):
                db.update_reservations_new_status(user['reservation_account'], 1)

    def run_periodically(self, interval):
        while True:
            if not is_within_time_range(TIME_START_TIME, TIME_END_TIME):
                logging.info("[Check] --------------------Reached end time.不更新.---------------------")
            else:
                logging.info(f"-----------------------------{get_current_hour()}--------------------------------")
                # 建立连接
                db = DatabaseManager()
                # 读取数据 获取用户信息
                users = db.fetch_check_information()
                # 修复bug
                if len(users) > 0:
                    with ThreadPoolExecutor(max_workers=len(users)) as executor:
                        futures = []
                        for index, user in enumerate(users):
                            # 将每个用户的登录和预约作为一个任务提交到线程池
                            futures.append(executor.submit(self.check, user))
                else:
                    logging.info("[Check] --------------------No data不更新.---------------------")
            time.sleep(interval)

    def location_serve_main(self):
        self.run_periodically(self.TIME_Check_TIME)


if __name__ == '__main__':
    RS = ReservationCheckService()
    # 设置为守护线程，这样主线程结束时子线程也会结束
    thread = threading.Thread(target=RS.location_serve_main)
    thread.daemon = True
    # 启动学习通座位检查线程
    thread.start()
