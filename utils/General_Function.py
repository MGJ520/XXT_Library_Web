import os
import re
import socket
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import base64
from hashlib import md5
import random
from uuid import uuid1
from datetime import datetime, timedelta

from config import status


def AES_Encrypt(data):
    """
    使用AES-CBC模式加密数据

    Args:
        data: 需要加密的字符串数据

    Returns:
        str: base64编码的加密数据
    """
    key = b"u2oh6Vu^HWe4_AES"  # Convert to bytes
    iv = b"u2oh6Vu^HWe4_AES"  # Convert to bytes
    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(data.encode('utf-8')) + padder.finalize()
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
    enctext = base64.b64encode(encrypted_data).decode('utf-8')
    return enctext
    
def resort(submit_info):
    """
    对字典按键进行排序

    Args:
        submit_info: 需要排序的字典

    Returns:
        dict: 按键排序后的新字典
    """
    return {key: submit_info[key] for key in sorted(submit_info.keys())}

def enc(submit_info):
    """
    对提交信息进行特定格式的MD5加密

    Args:
        submit_info: 需要加密的字典信息

    Returns:
        str: MD5加密后的十六进制字符串
    """
    add = lambda x, y: x + y
    processed_info = resort(submit_info)
    needed = [add(add('[', key), '=' + value) + ']' for key, value in processed_info.items()]
    pattern = "%sd`~7^/>N4!Q#){''"
    needed.append(add('[', pattern) + ']')
    seq = ''.join(needed)
    return md5(seq.encode("utf-8")).hexdigest()


# 计算两个时间点的差值
def is_within_m_minutes(timestamp1, timestamp2, m):
    """
    判断两个时间戳是否在指定分钟数之内

    Args:
        timestamp1: 第一个毫秒时间戳
        timestamp2: 第二个毫秒时间戳
        m: 指定的分钟数

    Returns:
        bool: 是否在指定分钟数之内
    """
    time1 = timestamp1 / 1000
    time2 = timestamp2 / 1000
    # 计算两个时间戳的差值，并转换为分钟
    time_diff_minutes = abs(time1 - time2) / 60
    # 判断时间差是否在m分钟之内
    return time_diff_minutes <= m

# time1是当前时间，如果大于当前时间，且在范围内
def is_within_m_minutes_num(timestamp1, timestamp2, m):
    """
    判断timestamp1是否大于timestamp2且在指定时间范围内

    Args:
        timestamp1: 当前时间戳(毫秒)
        timestamp2: 比较时间戳(毫秒)
        m: 指定的秒数

    Returns:
        bool: 是否符合条件
    """
    time1 = timestamp1 / 1000
    time2 = timestamp2 / 1000

    if time1 -time2>= 0:
        # 计算两个时间戳的差值，并转换为分钟
        time_diff_minutes = abs(time1 - time2)/60
        # 判断时间差是否在m分钟之内
        return time_diff_minutes <= m
    else:
        return  False


def is_tomorrow(timestamp_ms):
    """
    判断给定时间戳是否为明天

    Args:
        timestamp_ms: 毫秒时间戳

    Returns:
        bool: 是否为明天
    """
    given_date = datetime.fromtimestamp(timestamp_ms / 1000.0)
    # 获取明天的日期
    tomorrow_date = datetime.now() + timedelta(days=1)
    # 比较两个日期是否相等（只比较日期部分，忽略时间部分）
    return given_date.date() == tomorrow_date.date()

def get_current_hour():
    """
    获取当前的小时和分钟

    Returns:
        str: 格式化的时间字符串，如 "14.05"
    """
    current_time = datetime.now()
    hour = current_time.hour
    minute = current_time.minute
    return f"{hour}.{minute:02d}"

def timedelta_to_time_str(td):
    """
    将timedelta对象转换为时间字符串

    Args:
        td: timedelta对象

    Returns:
        str: 格式化的时间字符串，如 "14:05"
    """
    start_time = datetime(1, 1, 1) + td
    return start_time.strftime("%H:%M")

def _fetch_env_variables(env_name, action):
    """
    获取环境变量的值

    Args:
        env_name: 环境变量名
        action: 是否获取环境变量的标志

    Returns:
        str: 环境变量的值或空字符串
    """
    try:
        return os.environ[env_name] if action else ""
    except KeyError:
        print(f"Environment variable {env_name} is not configured correctly.")
        return None

def get_user_credentials(action):
    """
    获取用户凭证信息

    Args:
        action: 是否获取凭证的标志

    Returns:
        tuple: 用户名和密码的元组
    """
    usernames = _fetch_env_variables('USERNAMES', action)
    passwords = _fetch_env_variables('PASSWORDS', action)
    return usernames, passwords

# 将字符串转换为datetime对象
def parse_time(time_str):
    return datetime.strptime(time_str, "%H:%M:%S")

def is_within_time_range(start_time_str, end_time_str):
    # 获取当前时间
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")  # 格式化为时分秒

    # 将字符串时间转换为datetime对象
    start_time = datetime.strptime(start_time_str, "%H:%M:%S")
    end_time = datetime.strptime(end_time_str, "%H:%M:%S")

    # 将当前时间也转换为datetime对象
    current_time_obj = datetime.strptime(current_time, "%H:%M:%S")

    # 判断当前时间是否在范围内
    if start_time <= current_time_obj <= end_time:
        return True
    else:
        return False

def get_local_ip():
    """
    获取本机的内网IP地址

    Returns:
        str: 本机的内网IP地址，如果无法获取则返回None
    """
    s=[]
    try:
        # 创建一个UDP套接字
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # 连接到一个外部IP（不会真正发送数据）
        s.connect(("8.8.8.8", 80))
        # 获取本机IP地址
        ip = s.getsockname()[0]
        return str(ip)
    except socket.error as e:
        print(f"获取本机IP地址失败: {e}")
        return None
    finally:
        # 确保套接字被关闭
        s.close()

def format_timedelta(td):
    """将 timedelta 转换为 'HH:MM' 格式"""
    if isinstance(td, timedelta):
        hours, remainder = divmod(td.seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        return f"{hours:02d}:{minutes:02d}"
    else:
        return "00:00"  # 默认值




def get_status_code_by_name(status_name):
    # 反转字典，将中文状态作为键，数字作为值
    reverse_status = {v: k for k, v in status.items()}
    """根据中文状态名称查询对应的数字键"""
    return reverse_status.get(status_name, None)


def is_today(date_str, date_format="%Y-%m-%d"):
    # 将字符串转换为日期对象
    date_obj = datetime.strptime(date_str, date_format).date()

    # 获取今天的日期对象
    today = datetime.today().date()

    # 比较两个日期对象
    return date_obj == today

def is_email(s):
    # 定义邮箱的正则表达式
    pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    # 使用 re.match 检查字符串是否符合正则表达式
    if re.match(pattern, s):
        return True
    else:
        return False

