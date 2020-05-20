# API/ml/views.py
import os
import ast
import zipfile
import logging
import datetime
from django.conf import settings
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from celery.task.control import revoke

from ..models.preprocessed_data import PreprocessedData
from ..models.train_info import TrainInfo
from ..serializers.serializers import PreprocessedDataSerializer
from ..serializers.serializers import TrainModelSerializer
from ..services.model_train import tasks  # 비동기 처리로 할 작업들 불러오기
from ..services.model_train.train_helper import InspectUserRequest
from ..services.model_test.test_helper import ModelPerformance
from ...utils.custom_response import CustomErrorCode

logger = logging.getLogger("collect_log_view")
error_code = CustomErrorCode()


class TrainModelView(APIView):
    def post(self, request):
        user_request = request.data  # dict
        get_inspect_result = InspectUserRequest()

        query = TrainInfo.objects.all()
        if query.exists():
            get_pk_new = TrainInfo.objects.latest("MODEL_SEQUENCE_PK").pk + 1
        else:
            get_pk_new = 1

        # user_request가 valid하면 True 반환
        check_result = get_inspect_result.check_request_body_models_post(
            request_info=user_request, pk=get_pk_new)

        if isinstance(check_result, dict):  # check_result 타입이 dict이면 에러 메시지를 반환한 것!
            error_type = check_result["error_type"]
            error_msg = check_result["error_msg"]
            if error_type == "4004":
                return Response(error_code.FILE_NOT_FOUND_4004(path_info=error_msg),
                                status=status.HTTP_404_NOT_FOUND)
            elif error_type == "4101":
                return Response(error_code.MANDATORY_PARAMETER_MISSING_4101(error_msg),
                                status=status.HTTP_400_BAD_REQUEST)
            elif error_type == "4102":
                return Response(error_code.INVALID_PARAMETER_TYPE_4102(error_msg),
                                status=status.HTTP_400_BAD_REQUEST)
            elif error_type == "4022":
                return Response(error_code.UNPROCESSABLE_ENTITY_4022(error_msg),
                                status=status.HTTP_422_UNPROCESSABLE_ENTITY)
            elif error_type == "4103":
                return Response(error_code.INVALID_MODEL_PARAMETER_4103(error_msg),
                                status=status.HTTP_400_BAD_REQUEST)

        # 현재(2019.11) 분석 모듈은 전처리된 데이터만 학습에 요청함
        data_info = get_inspect_result.train_data_dict
        if get_inspect_result.train_data_type == "original":
            P_pk = None
            O_pk = data_info["ORIGINAL_DATA_SEQUENCE_FK1"]
            data_saved_path = data_info["FILEPATH"]
        elif get_inspect_result.train_data_type == "preprocessed":
            P_pk = data_info["PREPROCESSED_DATA_SEQUENCE_PK"]
            O_pk = data_info["ORIGINAL_DATA_SEQUENCE_FK1"]
            data_saved_path = data_info["FILEPATH"]

        result = tasks.model_train.apply_async(
            args=[user_request, data_saved_path, get_pk_new, "start"])
        logger.info(f"요청 ID [{get_pk_new}]의 모델 학습을 시작합니다")
        user_request.update({"model_parameters": get_inspect_result.model_param})
        user_request.update({"train_parameters": get_inspect_result.train_param})
        train_info = dict(
            COMMAND=str(user_request),
            JOB_ID=result.id,
            PROGRESS_STATE="ongoing",
            ORIGINAL_DATA_SEQUENCE_FK1=O_pk,
            PREPROCESSED_DATA_SEQUENCE_FK2=P_pk,
            PROGRESS_START_DATETIME=datetime.datetime.now())

        serializer = TrainModelSerializer(data=train_info)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        queryset = TrainInfo.objects.all().order_by("MODEL_SEQUENCE_PK")
        serializer = TrainModelSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TrainModelDetailView(APIView):
    def get(self, request, pk):
        train_info = get_object_or_404(TrainInfo, pk=pk)
        serializer = TrainModelSerializer(train_info)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, pk):
        train_info = get_object_or_404(TrainInfo, pk=pk)
        serializer = TrainModelSerializer(train_info)
        user_request = request.data  # dict

        get_inspect_result = InspectUserRequest()

        # user_request가 valid하면 True 반환
        check_result = get_inspect_result.check_patch_mode(request_info=user_request)
        if not check_result:  # check_result가 True아니면 에러 메시지를 반환한 것!
            error_type = check_result["error_type"]
            error_msg = check_result["error_msg"]
            if error_type == "4101":
                return Response(error_code.MANDATORY_PARAMETER_MISSING_4101(error_msg),
                                status=status.HTTP_400_BAD_REQUEST)
            elif error_type == "4102":
                return Response(error_code.INVALID_PARAMETER_TYPE_4102(error_msg),
                                status=status.HTTP_400_BAD_REQUEST)

        # 모델 삭제 여부 확인
        if serializer.data["DELETE_FLAG"]:
            return Response(
                error_code.CONFLICT_4009(mode="DELETE", error_msg="deleted"),
                status=status.HTTP_409_CONFLICT)

        # 수정하는 경우 1 = 모델 학습 중지
        elif "STOP" == user_request["mode"]:
            if serializer.data["PROGRESS_STATE"] == "success":
                return Response(
                    error_code.CONFLICT_4009(mode="STOP", error_msg="success"),
                    status=status.HTTP_409_CONFLICT)

            elif serializer.data["PROGRESS_STATE"] == "fail":
                return Response(
                    error_code.CONFLICT_4009(mode="STOP", error_msg="fail"),
                    status=status.HTTP_409_CONFLICT)

            else:  # 'ongoing'
                logger.info(f"요청 ID [{pk}]의 모델 학습을 중지합니다")
                job_id = serializer.data["JOB_ID"]
                revoke(job_id, terminate=True)

                stop_information = dict(
                    PROGRESS_STATE="standby",
                    PROGRESS_END_DATETIME=datetime.datetime.now())
                serializer = TrainModelSerializer(
                    train_info, data=stop_information, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Response(
                        {"request_id": pk, "progress_state": "standby"},
                        status=status.HTTP_200_OK)

        # 수정하는 경우 2 = 모델 재시작
        elif "RESTART" == user_request["mode"]:
            get_command = ast.literal_eval(serializer.data["COMMAND"])
            P_pk = get_command["train_data"]["preprocessed_data_sequence_pk"]
            P_serializer = PreprocessedDataSerializer(
                PreprocessedData.objects.get(pk=P_pk)).data
            data_saved_path = P_serializer["FILEPATH"]

            result = tasks.model_train.apply_async(
                args=[get_command, data_saved_path, pk, "restart"])
            logger.info(f"요청 ID [{pk}]의 모델 학습을 재시작합니다")
            change_info = dict(
                FILEPATH="",
                FILENAME="",
                TRAIN_SUMMARY="",
                VALIDATION_SUMMARY="",
                LOAD_STATE="model_not_found",
                PROGRESS_STATE="ongoing",
                JOB_ID=result.id,
                PROGRESS_START_DATETIME=datetime.datetime.now(),
                PROGRESS_END_DATETIME=None
            )
            serializer = TrainModelSerializer(train_info, data=change_info, partial=True)

            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # 데이터 전달 및 데이터 적용 테스트
        elif "TEST" == user_request["mode"]:
            if serializer.data["PROGRESS_STATE"] != "success":
                return Response(
                    error_code.CONFLICT_4009(
                        mode="TEST", error_msg=serializer.data["PROGRESS_STATE"]),
                        status=status.HTTP_409_CONFLICT)

            request_data_path = user_request["test_data_path"]
            if not os.path.isfile(request_data_path):
                return Response(
                    error_code.FILE_NOT_FOUND_4004(path_info=request_data_path),
                    status=status.HTTP_404_NOT_FOUND)

            # 예측값과 스코어를 같이 출력함
            logger.info(f"요청한 모델 ID [{pk}]의 테스트를 시작합니다")
            test_result = ModelPerformance(
                model_info=serializer.data,
                test_data_path=request_data_path
            )
            test_result = test_result.get_test_result()

            if "predict" not in test_result.keys():
                return Response(error_code.UNPROCESSABLE_ENTITY_4022(
                    error_msg=test_result["detail"]),
                    status=status.HTTP_422_UNPROCESSABLE_ENTITY)
            return Response(test_result, status=status.HTTP_200_OK)

    def delete(self, request, pk):
        # DELETE_FLAG == True로 전환하고, 저장된 모델 삭제 (db의 instance는 삭제하지 않음)
        # 이미 DELETE_FLAG가 True인 경우, Conflict(4009) 에러 반환
        train_info = get_object_or_404(TrainInfo, pk=pk)
        serializer = TrainModelSerializer(train_info)
        if serializer.data["DELETE_FLAG"]:
            return Response(error_code.CONFLICT_4009(mode="DELETE", error_msg="deleted"),
                            status=status.HTTP_409_CONFLICT)
        else:
            if os.path.isfile(serializer.data["FILEPATH"]):
                os.remove(serializer.data["FILEPATH"])
                serializer = TrainModelSerializer(
                    train_info, data=dict(DELETE_FLAG=True), partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(error_code.FILE_NOT_FOUND_4004(
                    path_info=serializer.data["FILEPATH"]),
                    status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
def model_download(request, pk):
    serializer = TrainModelSerializer(
        get_object_or_404(TrainInfo, pk=pk))
    if serializer.data["DELETE_FLAG"]:
        return Response(error_code.CONFLICT_4009(mode="DELETE", error_msg="deleted"),
                        status=status.HTTP_409_CONFLICT)
    response = HttpResponse(content_type="application/octet-stream")
    zip_file = zipfile.ZipFile(response, "w", compression=zipfile.ZIP_DEFLATED)
    zip_file.write(serializer.data["FILEPATH"], serializer.data["FILENAME"])
    zip_file.close()
    response["Content-Disposition"] = 'attachment; filename="M_{}.zip"'.format(pk)
    return response
