# API/ml/views.py
import os
import glob
import zipfile
import logging
import datetime
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from ..models.preprocessed_data import PreprocessedData
from ..serializers.serializers import PreprocessedDataSerializer
from ..services.data_preprocess import tasks
from ..services.data_preprocess.preprocess_helper import InspectUserRequest
from ..services.data_preprocess.preprocess_download import PreprocessedDownload
from ..services.data_preprocess.preprocess_download import DeletedInstanceError, InvalidParameterError, FileNotExistedError
from ...utils.custom_response import CustomErrorCode

logger = logging.getLogger("collect_log_view")
error_code = CustomErrorCode()


class PreprocessedDataView(APIView):
    def post(self, request):
        user_request = request.data
        get_inspect_result = InspectUserRequest()

        check_result = get_inspect_result.check_post_mode(request_info=user_request)
        if isinstance(check_result, dict):
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

        query = PreprocessedData.objects.all()
        if query.exists():
            get_pk_new = PreprocessedData.objects.latest("PREPROCESSED_DATA_SEQUENCE_PK").pk + 1
        else:
            get_pk_new = 1

        result = tasks.transformer_fit.apply_async(
            args=[get_inspect_result.data_saved_path, user_request, get_pk_new])
        logger.info(f"요청 ID [{get_pk_new}]의 전처리 작업을 시작합니다")
        info_save = dict(
            COMMAND=str(request.data),
            PROGRESS_STATE="ongoing",
            PROGRESS_START_DATETIME=datetime.datetime.now(),
            COLUMNS="N/A",
            STATISTICS="N/A",
            SAMPLE_DATA="N/A",
            AMOUNT=0,
            ORIGINAL_DATA_SEQUENCE_FK1=get_inspect_result.original_data_id,
        )

        serializer = PreprocessedDataSerializer(data=info_save)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        queryset = PreprocessedData.objects.all().order_by("PREPROCESSED_DATA_SEQUENCE_PK")
        serializer = PreprocessedDataSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class PreprocessedDataDetailView(APIView):
    def get(self, request, pk):
        preprocessed_data = get_object_or_404(PreprocessedData, pk=pk)
        serializer = PreprocessedDataSerializer(preprocessed_data)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk):
        # DELETE_FLAG == True 전환하고, 저장된 파일 삭제 (db의 instance 삭제하지 않음)
        # 이미 DELETE_FLAG 가 True 경우, Conflict(4009) 에러 반환
        preprocessed_data = get_object_or_404(PreprocessedData, pk=pk)
        serializer = PreprocessedDataSerializer(preprocessed_data)
        if serializer.data["DELETE_FLAG"]:
            return Response(
                error_code.CONFLICT_4009(mode="DELETE", error_msg="deleted"),
                status=status.HTTP_409_CONFLICT)
        else:
            # 데이터 전처리에 사용했던 기능들 저장 경로
            transformer_list = glob.glob(
                "result/preprocess_transformer/T_{}_*.pickle".format(pk)
            )
            if os.path.isfile(serializer.data["FILEPATH"]):
                os.remove(serializer.data["FILEPATH"])
                # 전처리된 데이터 파일 삭제
                for transformer_file in transformer_list:
                    os.remove(transformer_file)
                    # 전처리에 사용된 전처리기 삭제
                serializer = PreprocessedDataSerializer(
                    preprocessed_data, data=dict(DELETE_FLAG=True), partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(error_code.FILE_NOT_FOUND_4004(
                    path_info=serializer.data["FILEPATH"]),
                    status=status.HTTP_404_NOT_FOUND)


@api_view(["GET"])
def preprocessed_download(request, pk):
    try:
        get_type = request.GET["type"]
    except :
        return Response(
            error_code.MANDATORY_PARAMETER_MISSING_4101(error_msg="type"),
            status=status.HTTP_400_BAD_REQUEST)

    try:
        obj = PreprocessedDownload(pk=pk)

        response = HttpResponse(content_type="application/octet-stream")
        zip_file = zipfile.ZipFile(response, "w", compression=zipfile.ZIP_DEFLATED)
       
        if get_type == 'data':
            filepath, filename = obj.case_get(case=get_type)
            zip_file.write(filepath, filename)
            zip_file.close()
            response['Content-Disposition'] = 'attachment; filename="P_{}.zip"'.format(pk)

        elif get_type == 'transformer':
            pk_savad_list = obj.case_get(case=get_type)
            for filepath in pk_savad_list:
                zip_file.write(filepath, os.path.basename(filepath))
            zip_file.close()
            response["Content-Disposition"] = 'attachment; filename="T_{}.zip"'.format(pk)

        else:
            raise InvalidParameterError

    except DeletedInstanceError as e:
        return Response(
                error_code.CONFLICT_4009(mode="DELETE", error_msg="deleted"),
                status=status.HTTP_409_CONFLICT)
    except InvalidParameterError as e:
        return Response(
                error_code.INVALID_PARAMETER_TYPE_4102(error_msg=get_type), 
                status=status.HTTP_400_BAD_REQUEST)
    except FileNotExistedError as e:
        return Response(
            error_code.UNPROCESSABLE_ENTITY_4022(
                error_msg="Saved Preprocess Funtion is Not Existed"),
            status=status.HTTP_422_UNPROCESSABLE_ENTITY)
    return response

