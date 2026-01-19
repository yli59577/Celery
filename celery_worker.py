# celery_worker.py
from celery import Celery, Task
import time
import os

# 從環境變數讀取 Redis 連線，如果沒有則使用 localhost
CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://localhost:16379/0')
CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:16379/0')

celery_app = Celery(
    'tasks',
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    task_track_started=True,
)



class EchoTask(Task):
    """回傳輸入文字的任務"""
    name = 'tasks.echo_task_class'
    
    def run(self, text):
        return text



@celery_app.task
def add_task(a, b):
    """加法任務，模擬耗時操作"""
    time.sleep(5)  # 模擬耗時 5 秒
    return a + b


# 註冊 class-based task
celery_app.register_task(EchoTask())
