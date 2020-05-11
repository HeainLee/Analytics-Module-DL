#################[데이터 원본(학습데이터) 관리]#################
import os
import zipfile
import shutil
import logging
from django.conf import settings
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from ..models.original_data import OriginalData
from ..serializers.serializers import OriginalDataSerializer
from ..services.data_preprocess.preprocess_tester import TestPreprocessor
from ..services.data_preprocess.data_summary import DataSummary
from ..services.utils.custom_response import CustomErrorCode
from ..config.result_path_config import PATH_CONFIG

logger = logging.getLogger("collect_log_view")
error_code = CustomErrorCode()


class OriginalDataView(APIView):
    def post(self, request):
        data_save_path = PATH_CONFIG.ORIGINAL_DATA_DIRECTORY  # 'result/original_data'

        if "data_path" not in request.data.keys():
            return Response(
                error_code.MANDATORY_PARAMETER_MISSING_4101(error_msg="data_path"),
                status=status.HTTP_400_BAD_REQUEST)

        request_data_path = request.data["data_path"]
        if os.path.isfile(request_data_path):
            file_name = os.path.split(request_data_path)[1]
            file_ext = os.path.splitext(file_name)[1][1:]
        else:
            return Response(
                error_code.FILE_NOT_FOUND_4004(path_info=request_data_path),
                status=status.HTTP_404_NOT_FOUND)

        query = OriginalData.objects.all()
        if query.exists():
            get_pk_new = OriginalData.objects.latest("ORIGINAL_DATA_SEQUENCE_PK").pk + 1
        else:
            get_pk_new = 1

        save_file_name = os.path.join(
            data_save_path, "O_{}.{}".format(get_pk_new, file_ext))
        save_file_name = shutil.copy(request_data_path, save_file_name)
        data_summary = DataSummary(save_file_name)

        data_info = dict(
            NAME=os.path.splitext(file_name)[0],
            FILEPATH=save_file_name,
            FILENAME=os.path.splitext(os.path.split(save_file_name)[1])[0],
            EXTENSION=file_ext,
            COLUMNS=data_summary.columns_info(),
            STATISTICS=data_summary.statistics_info(),
            SAMPLE_DATA=data_summary.sample_info(),
            AMOUNT=data_summary.size_info(),
        )

        serializer = OriginalDataSerializer(data=data_info)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        queryset = OriginalData.objects.all().order_by("ORIGINAL_DATA_SEQUENCE_PK")
        serializer = OriginalDataSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class OriginalDataDetailView(APIView):
    def get(self, request, pk):
        origin_data = get_object_or_404(OriginalData, pk=pk)
        serializer = OriginalDataSerializer(origin_data)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, pk):
        # 지정한 원본데이터에 요청한 전처리를 수행하고 json 으로 넘겨줌
        user_request = request.data  # dict
        origin_data = get_object_or_404(OriginalData, pk=pk)
        serializer = OriginalDataSerializer(origin_data).data
        data_path = serializer["FILEPATH"]

        if not os.path.isfile(data_path):
            logger.error(f"{data_path} 경로가 존재하지 않습니다")
            return Response(error_code.FILE_NOT_FOUND_4004(path_info=data_path))

        test_preprocessor = TestPreprocessor(file_name=os.path.split(data_path)[1], pk=pk)
        check_result = test_preprocessor.check_request_body_original_patch(
            request_info=user_request)

        if isinstance(check_result, dict):
            error_type = check_result["error_type"]
            error_msg = check_result["error_msg"]
            if error_type == "4101":
                return Response(
                    error_code.MANDATORY_PARAMETER_MISSING_4101(error_msg),
                                status=status.HTTP_400_BAD_REQUEST)
            elif error_type == "4102":
                return Response(error_code.INVALID_PARAMETER_TYPE_4102(error_msg),
                                status=status.HTTP_400_BAD_REQUEST)

        # 전처리 테스트 수행 (요청을 하나씩 처리해서 한꺼번에 결과 반환)
        logger.info(f"요청 ID [{pk}]의 전처리 테스트를 시작합니다")
        preprocessed_test_result = test_preprocessor.test_result(
            request_info=user_request)

        if isinstance(preprocessed_test_result, dict):
            error_type = preprocessed_test_result["error_type"]
            error_msg = preprocessed_test_result["error_msg"]
            if error_type == "4102":  # ParameterSyntaxError
                return Response(
                    error_code.INVALID_PARAMETER_TYPE_4102(error_msg),
                    status=status.HTTP_400_BAD_REQUEST)
            elif error_type == "4104":  # PreprocessorTestError
                return Response(
                    error_code.INVALID_PREPROCESS_CONDITION_4104(error_msg),
                    status=status.HTTP_400_BAD_REQUEST)

        logger.info(f"요청 ID [{pk}]의 전처리 테스트가 완료되었습니다")
        return Response(preprocessed_test_result, status=status.HTTP_200_OK)

    def delete(self, request, pk):
        # DELETE_FLAG == True 전환하고, 저장된 파일 삭제 (db의 instance 삭제하지 않음)
        # 이미 DELETE_FLAG 가 True 경우, Conflict(4009) 에러 반환
        origin_data = get_object_or_404(OriginalData, pk=pk)
        serializer = OriginalDataSerializer(origin_data)
        if serializer.data["DELETE_FLAG"]:
            return Response(
                error_code.CONFLICT_4009(mode="DELETE", error_msg="deleted"),
                status=status.HTTP_409_CONFLICT)
        else:
            if os.path.isfile(serializer.data["FILEPATH"]):
                os.remove(serializer.data["FILEPATH"])
                serializer = OriginalDataSerializer(
                    origin_data, data=dict(DELETE_FLAG=True), partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(error_code.FILE_NOT_FOUND_4004(
                    path_info=serializer.data["FILEPATH"]),
                    status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
def original_data_download(request, pk):
    serializer = OriginalDataSerializer(
        get_object_or_404(OriginalData, pk=pk))
    if serializer.data['DELETE_FLAG']:
        return Response(error_code.CONFLICT_4009(mode='DELETE', error_msg='deleted'),
                        status=status.HTTP_409_CONFLICT)
    response = HttpResponse(content_type='application/octet-stream')
    zip_file = zipfile.ZipFile(response, 'w', compression=zipfile.ZIP_DEFLATED)
    zip_file.write(serializer.data['FILEPATH'], serializer.data['FILENAME'])
    zip_file.close()
    response['Content-Disposition'] = 'attachment; filename="O_{}.zip"'.format(pk)
    return response
