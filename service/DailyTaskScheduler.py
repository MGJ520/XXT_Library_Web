import time
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler

from service.Booking_Service import BookingService


class DailyTaskScheduler:
    def __init__(self, SUB_TIME):
        self.SUB_TIME = SUB_TIME
        self.scheduler = BackgroundScheduler()

    def job(self):
        print(f"任务运行中... 当前时间：{datetime.now()}")
        BookingService()
        self.schedule_next_run()

    def schedule_next_run(self):
        # 获取当前时间
        now = datetime.now()
        # 将目标时间字符串解析为时间
        target_hour, target_minute, target_second = map(int, self.SUB_TIME.split(":"))
        # 组合今天的日期和目标时间
        target_time_today = now.replace(hour=target_hour, minute=target_minute, second=target_second, microsecond=0)
        # 如果当前时间还没到目标时间，则调度今天的时间
        if now < target_time_today:
            next_run_time = target_time_today
        else:
            # 否则，调度明天的时间
            tomorrow = now + timedelta(days=1)
            next_run_time = tomorrow.replace(hour=target_hour, minute=target_minute, second=target_second,microsecond=0)
        # 添加任务
        self.scheduler.add_job(self.job, 'date', run_date=next_run_time)
        print(f"下一次任务将在 {next_run_time} 运行。")

    def start(self):
        # 首次调度任务
        self.schedule_next_run()
        # 启动调度器
        self.scheduler.start()
