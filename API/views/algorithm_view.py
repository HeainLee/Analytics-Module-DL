#######################[알고리즘 조회]#########################
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from ..models.algorithm import Algorithm
from ..serializers.serializers import ALGOSerializer


class AlgorithmView(APIView):
    def get(self, request):
        queryset = Algorithm.objects.all().order_by('ALGORITHM_SEQUENCE_PK')
        serializer = ALGOSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AlgorithmDetailView(APIView):
    def get(self, request, pk):
        algo_data = get_object_or_404(Algorithm, pk=pk)
        serializer = ALGOSerializer(algo_data)
        return Response(serializer.data, status=status.HTTP_200_OK)
