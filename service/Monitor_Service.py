import threading
from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from datetime import datetime
import psutil
import time




class MonitorService:
    def __init__(self):
        # 初始化网络计数器
        self.last_net_io = psutil.net_io_counters()

    def get_cpu_info(self):
        cpu_usage = psutil.cpu_percent(interval=1, percpu=False)
        cpu_count = psutil.cpu_count(logical=False)
        return {
            'cpu_usage': cpu_usage,
            'cpu_count': cpu_count
        }

    def get_memory_info(self):
        memory = psutil.virtual_memory()
        return {
            'total_memory': memory.total,
            'used_memory': memory.used,
            'free_memory': memory.free,
            'memory_percent': memory.percent
        }

    def get_disk_info(self):
        disk_info = {}
        for disk in psutil.disk_partitions():
            usage = psutil.disk_usage(disk.mountpoint)
            disk_info[disk.device] = {
                'total': usage.total,
                'used': usage.used,
                'free': usage.free,
                'percent': usage.percent
            }
        return disk_info

    def get_network_info(self):
        net_io = psutil.net_io_counters()
        bytes_sent = net_io.bytes_sent - self.last_net_io.bytes_sent
        bytes_recv = net_io.bytes_recv - self.last_net_io.bytes_recv
        self.last_net_io = net_io
        return {
            'bytes_sent': bytes_sent,
            'bytes_recv': bytes_recv
        }

    def get_process_info(self):
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'username', 'cpu_percent', 'memory_percent']):
            processes.append(proc.info)
        return sorted(processes, key=lambda proc: proc['cpu_percent'], reverse=True)[:10]

    def background_task(self):
        start_time = time.time()
        cpu_info = self.get_cpu_info()
        memory_info = self.get_memory_info()
        network_info = self.get_network_info()
        processes_info = self.get_process_info()

        elapsed_time = time.time() - start_time

        data = {
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'cpu_usage': cpu_info['cpu_usage'],
            'cpu_count': cpu_info['cpu_count'],
            'memory_percent': memory_info['memory_percent'],
            'total_memory': memory_info['total_memory'] / (1024 ** 3),
            'free_memory': memory_info['free_memory'] / (1024 ** 3),
            'network_sent': (network_info['bytes_sent'] / (1024 ** 2)) / elapsed_time,
            'network_recv': (network_info['bytes_recv'] / (1024 ** 2)) / elapsed_time,
            'processes': processes_info
        }
        return data


