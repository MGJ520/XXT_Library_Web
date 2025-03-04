from flask import jsonify

from config import LOW_MAX_REQUESTS, LOW_REQUEST_TIME_WINDOW
from service.Monitor_Service import MonitorService
from . import admin
# 实例化 MonitorService
monitor_service = MonitorService()

@admin.route('/api/get/system_info', methods=['GET'])
def get_system_info():
    data = monitor_service.background_task()
    return jsonify(data)