"""
celery 로 처리할 작업을 정의
스마트시티 분석 모듈에서는 모델학습(TRAIN MODEL) 작업을 처리할 때 사용
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

from .train_helper import MachineLearningTask
from ...models.train_info import TrainInfo
from ...serializers.serializers import TrainModelSerializer
from ....utils.custom_decorator import where_exception

logger = logging.getLogger("collect_log_task")


@shared_task(name="train_tasks.model_train", bind=True, ignore_result=False, track_started=True)
def model_train(self, train_info=None, data_saved_path=None, pk=None, mode=None):
    logger.info(f"요청 ID [{pk}]의 모델 학습이 진행중입니다")

    try:
        back_job = model_train_result(
            train_info=train_info, data_saved_path=data_saved_path, pk=pk, mode=mode
        )

        train_info = TrainInfo.objects.get(pk=pk)
        train_information = {}

        if not back_job:
            train_information["PROGRESS_STATE"] = "fail"
            train_information["PROGRESS_END_DATETIME"] = datetime.datetime.now()
            logger.error(f"요청 ID [{pk}]의 모델 학습이 실패했습니다")
            serializer = TrainModelSerializer(
                train_info, data=train_information, partial=True
            )
            if serializer.is_valid():
                serializer.save()
                return "task_failed"
            else:
                logger.info(f"요청 ID [{pk}]의 모델 학습이 실패했습니다")
                return "save_failed"

        else:
            train_information["FILEPATH"] = str(back_job["file_path"])
            train_information["FILENAME"] = str(back_job["file_name"])
            train_information["TRAIN_SUMMARY"] = str(back_job["model_info"])
            train_information["VALIDATION_SUMMARY"] = str(back_job["validation_info"])
            train_information["PROGRESS_STATE"] = "success"
            train_information["LOAD_STATE"] = "load_available"
            train_information["PROGRESS_END_DATETIME"] = datetime.datetime.now()
            logger.info(f"요청 ID [{pk}]의 모델 학습이 완료되었습니다")
            serializer = TrainModelSerializer(
                train_info, data=train_information, partial=True
            )
        if serializer.is_valid():
            serializer.save()
            return "async_task_finished"
        else:
            logger.info(f"요청 ID [{pk}]의 모델 저장이 실패했습니다 [모델 학습 정보] = {train_information}")
            return "save_failed"
    except Exception as e:
        where_exception(error_msg=e)


def model_train_result(train_info=None, data_saved_path=None, pk=None, mode=None):
    sk_asyn_task = MachineLearningTask()

    try:
        # time.sleep(15)
        logger.info(f"요청 ID [{pk}]의 모델 학습 모드는 [{mode}] 입니다")

        model_param = (
            train_info["model_parameters"]
            if "model_parameters" in train_info.keys()
            else None
        )
        train_param = train_info["train_parameters"]

        if mode == "restart":
            model_param = sk_asyn_task.check_params(params_dict=model_param)
            train_param = sk_asyn_task.check_params(params_dict=train_param)
        get_result = sk_asyn_task.model_task_result(
            algo_pk=train_info["algorithms_sequence_pk"],
            data_path=data_saved_path,
            model_param=model_param,
            train_param=train_param,
            pk=pk,
        )

        return get_result
    except Exception as e:
        where_exception(error_msg=e)
        return False
