# API/dl/views
import os
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view

class TrainModelView(APIView):
    def post(self, request):
        user_request = request.data
        return Response("전이학습 모델 생성", status=status.HTTP_200_OK)

    def get(self, request):
        return Response("전이학습 모델 조회", status=status.HTTP_200_OK)


class TrainModelDetailView(APIView):
    def get(self, request, pk):
        user_request = request.data
        return Response("전이학습 모델 개별 조회", status=status.HTTP_200_OK)

    def patch(self, request, pk):
        user_request = request.data
        return Response("전이학습 모델 개별 수정", status=status.HTTP_200_OK)

    def delete(self, request, pk):
        user_request = request.data
        return Response("전이학습 모델 삭제", status=status.HTTP_200_OK)

@api_view(['GET'])
def model_download(request, pk):
    user_request = request.data
    return Response("전이학습 모델 다운로드", status=status.HTTP_200_OK)
