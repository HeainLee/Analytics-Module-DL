# API/common/views.py
import json
import logging

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ObjectDoesNotExist

from ..models.health_info import HealthInfo
from ..serializers.serializers import HealthInfoSerializer
from ..services.health_check import tasks # 비동기 처리로 할 작업들 불러오기 이 부분에서 호출을 해야지, Celery 실행할 떄 인식이 됨..
from ...utils.custom_response import CustomErrorCode

logger = logging.getLogger('collect_log_view')
error_code = CustomErrorCode()

class HealthCheckView(APIView):
    def get(self, request):

        try:
            queryset = HealthInfo.objects.get(identifier="SERVER_HEALTH")
            print(queryset)
            serializer = HealthInfoSerializer(queryset, many=False)
        except ObjectDoesNotExist as e:
            return Response(error_code.RESOURCE_NOT_INITIATED_4051(
                error_msg="HealthCheck doesn't initiated check the celery worker or beat!"),
                status=status.HTTP_451_UNAVAILABLE_FOR_LEGAL_REASONS)

        serialized_data = serializer.data
        health_info = serializer.data['HEALTH_INFO']

        serialized_data['HEALTH_INFO'] = json.loads(health_info)

        # Return the manipulated dict
        return Response(serialized_data, status=status.HTTP_200_OK)

