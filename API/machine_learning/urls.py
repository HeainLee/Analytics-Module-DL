# API/ml
from django.urls import path
from django.conf import settings

from .views.original_data_view import OriginalDataView, OriginalDataDetailView, original_data_download
from .views.preprocessed_data_view import PreprocessedDataView, PreprocessedDataDetailView, preprocessed_download
from .views.train_model_view import TrainModelView, TrainModelDetailView, model_download

urlpatterns = [

    #################[데이터 원본(학습데이터) 관리]#################
    path('originalData', OriginalDataView.as_view()),
    path('originalData/<pk>', OriginalDataDetailView.as_view()),
    path('originalData/<pk>/download', original_data_download),
    #####################[전처리 데이터 관리]####################
    path('preprocessedData', PreprocessedDataView.as_view()),
    path('preprocessedData/<pk>', PreprocessedDataDetailView.as_view()),
    path('preprocessedData/<pk>/download', preprocessed_download),
    #########################[모델 생성]#######################
    path('model', TrainModelView.as_view()),
    path('model/<pk>', TrainModelDetailView.as_view()),
    path('model/<pk>/download', model_download),
]

