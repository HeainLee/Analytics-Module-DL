# API/serializers.py
from rest_framework import serializers

from ..models.algorithm import Algorithm
from ..models.original_data import OriginalData
from ..models.preprocess_functions import PreprocessFunction
from ..models.preprocessed_data import PreprocessedData
from ..models.train_info import TrainInfo
from ..models.health_info import HealthInfo

class ALGOSerializer(serializers.ModelSerializer):
    class Meta:
        model = Algorithm
        fields = '__all__'

class OriginalDataSerializer(serializers.ModelSerializer):
   class Meta:
        model = OriginalData
        fields = '__all__'

class PreprocessFunctionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PreprocessFunction
        fields = '__all__'

class PreprocessedDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = PreprocessedData
        fields = '__all__'
        
class TrainModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainInfo
        fields = '__all__'

class HealthInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = HealthInfo
        fields = '__all__'
