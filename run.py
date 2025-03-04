# run.py
from app import create_app
from config import WEB_SERVER_PORT, SUB_TIME
from service.Check_Service import ReservationCheckService
from service.DailyTaskScheduler import DailyTaskScheduler
from utils.Database_Function import DatabaseManager
from utils.General_Function import get_local_ip


app = create_app()


def web_service():
    local_ip = get_local_ip()
    if local_ip:
        print(f"本机内网IP地址: {local_ip}")
        # 使用获取到的IP地址启动Flask应用
        app.run(host=local_ip, port=WEB_SERVER_PORT, debug=False)
    else:
        print("无法获取本机内网IP地址。")
        # 如果无法获取IP地址，不传递 host 参数，使用默认的 localhost 启动
        app.run(port=WEB_SERVER_PORT, debug=False)

def booking_service():
    scheduler = DailyTaskScheduler(SUB_TIME)
    scheduler.start()


# ------------------------------主函数-----------------------------------
if __name__ == '__main__':
    # 数据库初始化
    DatabaseManager()
    # 检查服务
    ReservationCheckService()
    # 预约服务
    booking_service()
    # Web服务
    web_service()

