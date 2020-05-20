# API/dl
from django.urls import path
from django.conf import settings

from .views.original_data_view import OriginalDataView, OriginalDataDetailView
from .views.train_model_view import TrainModelView, TrainModelDetailView, model_download

urlpatterns = [

    #################[데이터 원본 관리]#########################
    path('originalData', OriginalDataView.as_view()),
    path('originalData/<pk>', OriginalDataDetailView.as_view()),
    #########################[모델 생성]#######################
    path('model', TrainModelView.as_view()),
    path('model/<pk>', TrainModelDetailView.as_view()),
    path('model/<pk>/download', model_download),
]

