# API/common.py
from django.urls import path
from django.conf import settings

from .views.algorithm_view import AlgorithmView, AlgorithmDetailView
from .views.preprocess_function_view import PreprocessFunctionView, PreprocessFunctionDetailView
from .views.localfile_view import LocalFileView
from .views.health_check_view import HealthCheckView

urlpatterns = [

    #######################[알고리즘 조회]######################
    path('algorithm', AlgorithmView.as_view()),
    path('algorithm/<pk>', AlgorithmDetailView.as_view()),
    ######################[전처리 방법 조회]#####################
    path('preprocessFunction', PreprocessFunctionView.as_view()),
    path('preprocessFunction/<pk>', PreprocessFunctionDetailView.as_view()),
    ###############[로컬 파일 리스트/샘플 조회]####################
    path('localFile', LocalFileView.as_view()),
    #########################[헬스 체크]#######################
    path('healthCheck', HealthCheckView.as_view()),
]

