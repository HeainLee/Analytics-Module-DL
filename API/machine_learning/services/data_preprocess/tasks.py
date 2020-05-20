"""
celery 로 처리할 작업을 정의
스마트시티 분석 모듈에서는 전처리된 데이터를 생성하는 작업을 처리할 때 사용
@shared_task 데코레이터 = 해당 함수에 대한 요청이 들어오며 작업을 할당
"""
from __future__ import absolute_import
from multiprocessing import current_process

try:
    current_process()._config
except AttributeError:
    current_process()._config = {"semprefix": "/mp"}

import logging
import datetime
from celery import shared_task
from dasolution.celery import app

from .preprocess_helper import PreprocessTask
from ...models.preprocessed_data import PreprocessedData
from ...serializers.serializers import PreprocessedDataSerializer
from ....utils.custom_decorator import where_exception

logger = logging.getLogger("collect_log_task")


@shared_task(name="preprocess_tasks.transformer_fit", bind=True, ignore_result=False, track_started=True)
def transformer_fit(self, data_saved_path=None, pfunction_info=None, pk=None):
    logger.info(f"요청 ID [{pk}]의 전처리 작업이 진행중입니다")

    try:
        get_result = PreprocessTask()
        back_job = get_result.task_result(
            data_path=data_saved_path, request_info=pfunction_info, pk=pk
        )

        Pdata_info = PreprocessedData.objects.get(pk=pk)
        fit_information = {}

        if not back_job:
            fit_information["PROGRESS_STATE"] = "fail"
            fit_information["PROGRESS_END_DATETIME"] = datetime.datetime.now()
            logger.error(f"요청 ID [{pk}]의 전처리 작업이 실패했습니다")
            serializer = PreprocessedDataSerializer(
                Pdata_info, data=fit_information, partial=True
            )
        else:
            fit_information["FILEPATH"] = str(back_job["file_path"])  # 생성된 데이터의 위치
            fit_information["FILENAME"] = str(back_job["file_name"])  # 생성된 데이터의 파일명
            fit_information["SUMMARY"] = str(back_job["summary"])  # 전처리를 수행한 것에 대한 정보 모음
            fit_information["COLUMNS"] = back_job["columns_info"]
            fit_information["AMOUNT"] = back_job["amount_info"]
            fit_information["SAMPLE_DATA"] = back_job["sample_data"]
            fit_information["STATISTICS"] = back_job["statistics"]
            fit_information["PROGRESS_STATE"] = "success"
            fit_information["PROGRESS_END_DATETIME"] = datetime.datetime.now()
            logger.info(f"요청 ID [{pk}]의 전처리 작업이 완료되었습니다")
            serializer = PreprocessedDataSerializer(
                Pdata_info, data=fit_information, partial=True
            )
        if serializer.is_valid():
            serializer.save()
            return "async_task_finished"
        else:
            logger.error(f"요청 ID [{pk}]의 전처리 데이터 저장이 실패했습니다")
            return "save_failed"
    except Exception as e:
        where_exception(error_msg=e)
        return False
