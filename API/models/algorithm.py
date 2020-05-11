######################[분석 가능한 알고리즘 관련]#######################
from django.db import models

class Algorithm(models.Model):
    ALGORITHM_SEQUENCE_PK = models.BigIntegerField(primary_key=True, unique=True)
    ALGORITHM_NAME = models.CharField(max_length=100)
    LIBRARY_NAME = models.CharField(max_length=100)
    LIBRARY_VERSION = models.CharField(max_length=50, blank=True)
    LIBRARY_DOCUMENT_URL = models.CharField(max_length=200, blank=True)
    LIBRARY_OBJECT_NAME = models.CharField(max_length=50)
    LIBRARY_FUNCTION_NAME = models.CharField(max_length=50)
    LIBRARY_FUNCTION_DESCRIPTION = models.CharField(max_length=500, blank=True)
    LIBRARY_FUNCTION_USAGE = models.CharField(max_length=50)
    MODEL_PARAMETERS = models.TextField()
    TRAIN_PARAMETERS = models.TextField()
    SUPPORT_DATA_TYPE = models.CharField(max_length=200, blank=True)
    CREATE_DATETIME = models.DateTimeField(auto_now_add=True)
    WRITER = models.CharField(max_length=50)
    USE_FLAG = models.BooleanField(default=True)

    class Meta:
        managed = True
        db_table = 'ALGORITHM'