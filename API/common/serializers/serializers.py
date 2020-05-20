# API/common/serializers.py
from rest_framework import serializers

from ..models.algorithm import Algorithm
from ..models.preprocess_function import PreprocessFunction
from ..models.health_info import HealthInfo

class ALGOSerializer(serializers.ModelSerializer):
    class Meta:
        model = Algorithm
        fields = '__all__'

class PreprocessFunctionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PreprocessFunction
        fields = '__all__'

class HealthInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = HealthInfo
        fields = '__all__'
