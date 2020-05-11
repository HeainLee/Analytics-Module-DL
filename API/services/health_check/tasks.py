'''
celery로 처리할 작업을 정의
스마트시티 분석 모듈에서는 Health 상태를 스케줄링 작업 처리할 때 사용
@shared_task 데코레이터 = 해당 함수에 대한 요청이 들어오며 작업을 할당
'''
from __future__ import absolute_import
from multiprocessing import current_process  
try:
    current_process()._config
except AttributeError:
    current_process()._config = {'semprefix': '/mp'}

import os
import sys
import time
import datetime
from celery import shared_task
from celery.task.control import revoke
from celery.utils.log import get_task_logger
from django.core.exceptions import ObjectDoesNotExist

from ...serializers.serializers import HealthInfoSerializer
from ...models.health_info import HealthInfo
from .health_check import HealthCheck

logger = get_task_logger(__name__)


@shared_task(name='health_check_tasks.health_check', bind=True, ignore_result=False, track_started=True)
def health_check(self):
    ## 현재의 서버 상태 값을 가져옴.
    healthCheck = HealthCheck()
    healthInfoJson = healthCheck.updateHeatlhInfo()

    try:
        e = HealthInfo.objects.get(identifier='SERVER_HEALTH')
        e.HEALTH_INFO = str(healthInfoJson)
        e.save()
        return "Successfully Data Updated to Database."

    except ObjectDoesNotExist:
        health_info = dict(identifier='SERVER_HEALTH', HEALTH_INFO=str(healthInfoJson))
        serializer = HealthInfoSerializer(data=health_info)

        if serializer.is_valid():
            serializer.save()
            return "Successfully Data Saved to Database."
        else:
            return serializer.errors






