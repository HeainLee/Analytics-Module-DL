from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from .views.algorithm_view import AlgorithmView, AlgorithmDetailView
from .views.localfile_view import localfile
from .views.original_data_view import OriginalDataView, OriginalDataDetailView
from .views.preprocess_function_view import PreprocessFunctionView, PreprocessFunctionDetailView
from .views.preprocessed_data_view import PreprocessedDataView, PreprocessedDataDetailView, preprocessed_download
from .views.train_model_view import TrainModelView, TrainModelDetailView, model_download
from .views.health_check_view import HealthCheckView
from .views.async_task_view import AsyncTask
#app_name = 'analysis'


urlpatterns = [
    #######################[알고리즘 조회]#########################
    path('algorithm', AlgorithmView.as_view()),
    path('algorithm/<pk>', AlgorithmDetailView.as_view()),
    
    ###############[샌드박스 안의 로컬 파일 리스트]#################
    path('localFiles', localfile.as_view()),

    #################[데이터 원본(학습데이터) 관리]#################
    path('originalData', OriginalDataView.as_view()),
    path('originalData/<pk>', OriginalDataDetailView.as_view()),

    ######################[전처리 방법 조회]#######################
    path('preprocessFunction', PreprocessFunctionView.as_view()),
    path('preprocessFunction/<pk>', PreprocessFunctionDetailView.as_view()),

    #####################[전처리 데이터 관리]######################
    path('preprocessedData', PreprocessedDataView.as_view()),
    path('preprocessedData/<pk>', PreprocessedDataDetailView.as_view()),
    path('preprocessedData/<pk>/download', preprocessed_download),

    #########################[모델 생성]##########################
    path('model', TrainModelView.as_view()),
    path('model/<pk>', TrainModelDetailView.as_view()),
    path('model/<pk>/download', model_download),

    #########################[헬스 체크]##########################
    path('healthCheck', HealthCheckView.as_view()),

    #########################[비동기작업 체크]##########################
    path('task', AsyncTask.as_view()),

]

