import json
import requests
import re
import time
import logging
import datetime
from urllib3.exceptions import InsecureRequestWarning
from utils.General_Function import AES_Encrypt, enc


class XxTWebApi:
    def __init__(self, sleep_time=0.2, max_attempt=3, enable_slider=False, reserve_next_day=False):
        # 登录页面
        self.login_page = "https://passport2.chaoxing.com/mlogin?loginType=1&newversion=true&fid="

        # 二维码座位页面
        self.seat_url = "https://office.chaoxing.com/front/third/apps/seat/code?id={}&seatNum={}"

        # 签到
        self.sign_url = "https://office.chaoxing.com/data/apps/seat/sign"

        # 退座
        self.sign_back_url = "https://office.chaoxing.com/data/apps/seat/signback"

        # 取消
        self.cancel_url = "https://office.chaoxing.com/data/apps/seat/cancel"

        # 预约
        self.submit_url = "https://office.chaoxing.com/data/apps/seat/submit"

        # 登录
        self.login_url = "https://passport2.chaoxing.com/fanyalogin"

        # 注意 老版本的系统需要将url中的seat改为seatengine
        self.seat_reservation_info_url="https://office.chaoxing.com/data/apps/seat/reservelist?indexId=0&pageSize=100&type=-1"

        self.headers = {
            "Referer": "https://office.chaoxing.com/",
            "Host": "captcha.chaoxing.com",
            "Pragma": 'no-cache',
            "Sec-Ch-Ua": '"Google Chrome";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Linux"',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'
        }

        self.login_headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
            "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 10_3_1 like Mac OS X) AppleWebKit/603.1.3 (KHTML, like Gecko) Version/10.0 Mobile/14E304 Safari/602.1 wechatdevtools/1.05.2109131 MicroMessenger/8.0.5 Language/zh_CN webview/16364215743155638",
            "X-Requested-With": "XMLHttpRequest",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Host": "passport2.chaoxing.com"
        }

        self.token = ""

        self.submit_msg = []

        self.requests = requests.session()

        self.sleep_time = sleep_time

        self.max_attempt = max_attempt

        self.enable_slider = enable_slider

        self.reserve_next_day = reserve_next_day

        self.status = {
            '0': '待履约',
            '1': '学习中',
            '2': '已履约',
            '3': '暂离中',
            '5': '被监督中',
            '7': '已取消',
        }

        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

    # login and page token
    def _get_page_token(self, url):
        response = self.requests.get(url=url, verify=False)
        html = response.content.decode('utf-8')
        token = re.findall(
            'token: \'(.*?)\'', html)[0] if len(re.findall('token: \'(.*?)\'', html)) > 0 else ""
        return token


    def get_login_status(self):
        self.requests.headers = self.login_headers
        self.requests.get(url=self.login_page, verify=False)


    def login(self, username, password):
        username_aes = AES_Encrypt(username)
        password_aes = AES_Encrypt(password)
        parm = {
            "fid": -1,
            "uname": username_aes,
            "password": password_aes,
            "refer": "http%3A%2F%2Foffice.chaoxing.com%2Ffront%2Fthird%2Fapps%2Fseat%2Fcode%3Fid%3D4219%26seatNum%3D380",
            "t": True
        }
        jsons = self.requests.post(url=self.login_url, params=parm, verify=False)
        obj = jsons.json()
        if obj['status']:
            return True, ''
        else:
            logging.error(f"[login] - User {username} login failed. Please check you password and username! {obj}")
            return False, obj['msg2']


    @classmethod
    def t_time(cls, timestamp):
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(str(timestamp)[0:10])))

    # 获取到最近一次预约座位ID
    def get_my_seat_id(self):
        response = self.requests.get(url=self.seat_reservation_info_url).json()['data']['reserveList']
        return response[0]['id']

    # 获全部预约记录
    def get_seat_reservation_info(self, username):
        response = self.requests.get(url=self.seat_reservation_info_url).json()['data']['reserveList']
        index = response[0]

        if index['type'] == -1:
            status_message = self.status[str(index['status'])]
        else:
            status_message = "违约"

        logging.info(f"[Get]--{username}--{index['firstLevelName']}--"
                     f"{index['secondLevelName']}--{index['thirdLevelName']}--{index['seatNum']}--"
                     f"{self.t_time(index['startTime'])}--{self.t_time(index['endTime'])}--{status_message}")

        return index



    # 签到
    def sign(self, username, times, roomid, seatid):
        # token = self._get_page_token(self.url.format(roomid, seatid))
        parm = {
            "id": self.get_my_seat_id()
            # "token": token
        }
        html = self.requests.post(url=self.sign_url, params=parm, verify=True).content.decode('utf-8')
        logging.info(f"[Sign]-- {username} -- {times} -- {roomid} -- {seatid} -- {json.loads(html)} ---")
        return json.loads(html)["success"]


    # 退座
    def sign_back(self, username, times, roomid, seatid):
        parm = {
            "id": self.get_my_seat_id()
        }
        html = self.requests.post(url=self.sign_back_url, params=parm, verify=True).content.decode('utf-8')
        logging.info(f"[Signback]-- {username} -- {times} -- {roomid} -- {seatid} -- {json.loads(html)} ---")
        return json.loads(html)["success"]


    def cancel(self, username, times, roomid, seatid):
        parm = {
            "id": self.get_my_seat_id()
        }
        html = self.requests.post(url=self.cancel_url, params=parm, verify=True).content.decode('utf-8')
        logging.info(f"[Cancel]-- {username} -- {times} -- {roomid} -- {seatid} -- {json.loads(html)} ---")
        return json.loads(html)["success"]


    # 预约提交
    def booking(self, url, times, token, room_id, seat_id, username, captcha="", action=False):
        delta_day = 1 if self.reserve_next_day else 0

        # 预约今天，修改days=1表示预约明天
        day = datetime.date.today() + datetime.timedelta(days=0 + delta_day)

        # 由于action时区问题导致其早+8区一天
        if action:
            day = datetime.date.today() + datetime.timedelta(days=1 + delta_day)

        parm = {
            "roomId": room_id,
            "startTime": times[0],
            "endTime": times[1],
            "day": str(day),
            "seatNum": seat_id,
            "captcha": captcha,
            "token": token
        }

        parm["enc"] = enc(parm)

        html = self.requests.post(url=url, params=parm, verify=True).content.decode('utf-8')


        # self.submit_msg.append(times[0] + "~" + times[1] + ':  ' + str(json.loads(html)))
        if json.loads(html)["success"]:
            logging.info(f"[Try_Booking_OKOK]-- {username} -- {times} -- {room_id} -- {seat_id} -- {json.loads(html)} ---")
        else:
            logging.info(f"[Try_Booking_False]-- {username} -- {times} -- {room_id} -- {seat_id} -- {json.loads(html)} ---")

        return json.loads(html)["success"]


    def _retry_action(self, action_func, *args, **kwargs):
        """
        通用的重试逻辑封装
        :param action_func: 需要重试的操作函数
        :param args: 操作函数的普通参数
        :param kwargs: 操作函数的关键字参数
        :return: 操作函数的返回值
        """
        suc = False
        while not suc and self.max_attempt > 0:
            suc = action_func(*args, **kwargs)
            if suc:
                return suc
            time.sleep(self.sleep_time)
            self.max_attempt -= 1
        return suc


    def submit_sign(self, username, times, roomid, seatid):
        return self._retry_action(self.sign, username=username, times=times, roomid=roomid, seatid=seatid)


    def submit_sign_back(self, username, times, roomid, seatid):
        return self._retry_action(self.sign_back, username=username, times=times, roomid=roomid, seatid=seatid)


    def submit_cancel(self, username, times, roomid, seatid):
        return self._retry_action(self.cancel, username=username, times=times, roomid=roomid, seatid=seatid)


    def submit_booking(self, times, room_id, seat_id, username):
        suc = False
        while not suc and self.max_attempt > 0:
            self.token = self._get_page_token(self.seat_url.format(room_id, seat_id))
            suc = self.booking(self.submit_url,
                               times=times,
                               token=self.token,
                               room_id=room_id,
                               seat_id=seat_id,
                               captcha="",
                               action=False,
                               username=username)
            if suc:
                return suc
            time.sleep(self.sleep_time)
            self.max_attempt -= 1
        return suc


