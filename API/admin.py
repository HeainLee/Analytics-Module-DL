from django.contrib import admin
from .models.algorithm import Algorithm
from .models.original_data import OriginalData
from .models.preprocess_functions import PreprocessFunction
from .models.preprocessed_data import PreprocessedData
from .models.train_info import TrainInfo

# Register your models here.

# 출력할 AlgorithmsAdmin 클래스를 만든다
class AlgorithmAdmin(admin.ModelAdmin):
    list_display = ('ALGORITHM_SEQUENCE_PK', 'ALGORITHM_NAME', 'LIBRARY_NAME', 'LIBRARY_VERSION')

class OriginalDataAdmin(admin.ModelAdmin):
    list_display = ('ORIGINAL_DATA_SEQUENCE_PK', 'NAME', 'FILEPATH', 'EXTENSION', 'CREATE_DATETIME')

class PreprocessFunctionAdmin(admin.ModelAdmin):
    list_display = ('PREPROCESS_FUNCTIONS_SEQUENCE_PK', 'PREPROCESS_FUNCTIONS_NAME', 'LIBRARY_NAME', 'LIBRARY_VERSION')

class PreProcessedDataAdmin(admin.ModelAdmin):
    list_display = ('PREPROCESSED_DATA_SEQUENCE_PK', 'FILENAME', 'FILEPATH', 'ORIGINAL_DATA_SEQUENCE_FK1', 'CREATE_DATETIME')

class TrainInfoAdmin(admin.ModelAdmin):
    list_display = ('MODEL_SEQUENCE_PK', 'PROGRESS_STATE', 'CREATE_DATETIME')

# 클래스를 어드민 사이트에 등록한다.
admin.site.register(Algorithm, AlgorithmAdmin)
admin.site.register(OriginalData, OriginalDataAdmin)
admin.site.register(PreprocessFunction, PreprocessFunctionAdmin)
admin.site.register(PreprocessedData, PreProcessedDataAdmin)
admin.site.register(TrainInfo, TrainInfoAdmin)

 