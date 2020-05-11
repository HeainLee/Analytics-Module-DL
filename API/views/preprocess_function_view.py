######################[전처리 방법 조회]#######################
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from ..models.preprocess_functions import PreprocessFunction
from ..serializers.serializers import PreprocessFunctionSerializer


class PreprocessFunctionView(APIView):
    def get(self, request):
        queryset = PreprocessFunction.objects.all().order_by('PREPROCESS_FUNCTIONS_SEQUENCE_PK')
        serializer = PreprocessFunctionSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class PreprocessFunctionDetailView(APIView):
    def get(self, request, pk):
        func_data = get_object_or_404(PreprocessFunction, pk=pk)
        serializer = PreprocessFunctionSerializer(func_data)
        return Response(serializer.data, status=status.HTTP_200_OK)
