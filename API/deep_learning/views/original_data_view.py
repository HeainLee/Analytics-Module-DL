# API/dl/views
import os
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

class OriginalDataView(APIView):
    def post(self, request):
        user_request = request.data
        return Response("이미지 원본데이터 생성", status=status.HTTP_200_OK)

    def get(self, request):
        return Response("이미지 원본데이터 조회", status=status.HTTP_200_OK)


class OriginalDataDetailView(APIView):
    def get(self, request, pk):
        user_request = request.data
        return Response("이미지 원본데이터 개별 조회", status=status.HTTP_200_OK)

    def delete(self, request, pk):
        user_request = request.data
        return Response("이미지 원본데이터 삭제", status=status.HTTP_200_OK)
