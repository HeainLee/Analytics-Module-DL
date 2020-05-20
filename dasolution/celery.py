from __future__ import absolute_import

import os
import django
import psutil
from celery import Celery
from datetime import timedelta
from django.apps import apps
from django.conf import settings
from celery.schedules import crontab

# Django의 세팅 모듈을 Celery의 기본으로 사용하도록 등록합니다.

# process = psutil.Process(pid)


def checkIfProcessRunning(processName):
    #Iterate over the all the running process 
    for proc in psutil.process_iter(attrs=["cmdline", "name"]):
        cmdline = proc.info['cmdline']
        if cmdline is not None:
            if processName in cmdline:
                return cmdline

check_version = checkIfProcessRunning('manage.py')

if check_version:
    print(' ')
    for cmd in check_version:
        
        if 'production' in cmd:
            os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dasolution.production')
            print('장고 환경을 "배포(production.py)" 버전으로 실행했습니다.')
        elif 'settings' in cmd:
            os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dasolution.settings')
            print('장고 환경을 "로컬(settings.py)" 버전으로 실행했습니다.')
else:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dasolution.settings')
    print('\n manage.py 명령어가 실행되지 않았습니다. "로컬(settings.py)" 버전의 환경을 임포트합니다.')

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dasolution.settings')
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dasolution.production')

from django.conf import settings  # noqa


app = Celery('dasolution', 
    backend="amqp", #결과를 보기 위해 backend 설정 필요 
    broker='amqp://guest@127.0.0.1:5672//', #현재 브로커 = rabbitmq
    )



# 문자열로 등록한 이유는 Celery Worker가 Windows를 사용할 경우 
# 객체를 pickle로 묶을 필요가 없다는 것을 알려주기 위함입니다.
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


app.conf.update(
    CELERY_TASK_SERIALIZER='json',
    CELERY_ACCEPT_CONTENT=['json'],  # Ignore other content
    CELERY_RESULT_SERIALIZER='json',
    CELERY_TIMEZONE='Asia/Seoul',
    CELERY_ENABLE_UTC=False,
    CELERYBEAT_SCHEDULE = {
        'say_hello-every-seconds': {
            "task": "health_check_tasks.health_check",
            'schedule': timedelta(seconds=30),
            'args': ()
        },
    }
)


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))


