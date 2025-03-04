import logging
import datetime
import threading
from concurrent.futures import ThreadPoolExecutor
import schedule
import time
from datetime import datetime, timedelta

from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime

from config import TIME_Check_TIME, TIME_MAX_ATTEMPT, TIME_SLEEP_TIME, TIME_START_TIME, TIME_END_TIME, SUB_SLEEP_TIME, \
    SUB_MAX_ATTEMPT, RESERVE_NEXT_DAY, SUB_TIME
from utils.Database_Function import DatabaseManager
from utils.Xxt_WebApi import XxTWebApi
from utils.General_Function import is_tomorrow, get_current_hour, \
    is_within_m_minutes, is_within_m_minutes_num, parse_time, is_within_time_range, is_today


class BookingService:
    def __init__(self):
        self.TIME_SLEEP_TIME = SUB_SLEEP_TIME
        self.TIME_MAX_ATTEMPT = SUB_MAX_ATTEMPT
        self.TIME_RESERVE_NEXT_DAY = RESERVE_NEXT_DAY
        self.task_map = {}
        # 配置日志的基本设置，设置日志级别为INFO，并定义日志的格式
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        # 设置为守护线程，这样主线程结束时子线程也会结束
        thread_rs = threading.Thread(target=self.location_serve_main)
        # thread_rs.daemon = True
        # 启动学习通座位检查线程
        thread_rs.start()

    # region _接口

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


    def sign_back(self, user):
        return self.perform_action(user, "sign_back")



    def check(self, reservation):
        db = DatabaseManager()
        user = db.fetch_check_more_information(reservation[0])[0]  # 获取列表中的第一个字典

        s = XxTWebApi(sleep_time=self.TIME_SLEEP_TIME, max_attempt=self.TIME_MAX_ATTEMPT,reserve_next_day=self.TIME_RESERVE_NEXT_DAY)
        s.get_login_status()
        out_login = s.login(user['reservation_account'], user['reservation_password'])

        # 密码错误
        if not out_login[0]:
            db.update_reservations_new_status(user['reservation_account'], 8)
            logging.info(f"[Try_Booking] 密码错误 ")
            return False


        s.requests.headers.update({'Host': 'office.chaoxing.com'})


        # 获取第一个信息
        Seat_info = s.get_seat_reservation_info(user['reservation_account'])

        # 待履约
        if Seat_info['status'] == 0:
           if not s.submit_cancel(account, 'time', user['room_location'], user['seat_location']):
               logging.info(f"[Try_Booking] 取消旧预约失败 ")
               return

        #学习中
        if Seat_info['status'] == 1:
            if not self.sign_back(user):
                logging.info(f"[Try_Booking] 取消学习失败 ")
                return

        logging.info(f"[Try_Booking] - {user['reservation_account']} -- {user['start_time']}-{user['end_time']}-- {user['room_location']} -- {user['seat_location']} ---- ")

        # 提交
        if s.submit_booking([str(user['start_time']),str(user['end_time'])], user['room_location'], user['seat_location'], user['reservation_account']):
            db.update_reservations_new_status(user['reservation_account'], 0)
    # endregion _接口

    def location_serve_main(self):
        db = DatabaseManager()
        # 读取数据 获取用户信息
        users = db.fetch_booking_information()
        # 修复bug
        if len(users) > 0:
            with ThreadPoolExecutor(max_workers=len(users)) as executor:
                futures = []
                for index, user in enumerate(users):
                    # 将每个用户的登录和预约作为一个任务提交到线程池
                    futures.append(executor.submit(self.check, user))
        else:
            logging.info("[Booking] --------------------No data不更新.---------------------")


if __name__ == '__main__':
    RS = BookingService()
    while True:
        time.sleep(1000)
        continue
