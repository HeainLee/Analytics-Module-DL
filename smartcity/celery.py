from __future__ import absolute_import

import os
import django
from celery import Celery
from datetime import timedelta
from django.apps import apps
from django.conf import settings
from celery.schedules import crontab

# Django의 세팅 모듈을 Celery의 기본으로 사용하도록 등록합니다.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smartcity.settings')

from django.conf import settings  # noqa


app = Celery('smartcity', 
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


