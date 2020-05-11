######################[사용자의 요청 정보를 db에 저장하는 모델]#######################
from django.db import models

class TrainInfo(models.Model):
    MODEL_SEQUENCE_PK = models.BigAutoField(primary_key=True, unique=True)
    COMMAND = models.TextField()
    FILEPATH = models.CharField(max_length=300, blank=True)
    FILENAME = models.CharField(max_length=100, blank=True)
    TRAIN_SUMMARY = models.TextField(blank=True)
    VALIDATION_SUMMARY = models.TextField(blank=True)
    CREATE_DATETIME = models.DateTimeField(auto_now_add=True)
    PROGRESS_STATE = models.CharField(max_length=30, default='standby')
    PROGRESS_START_DATETIME = models.DateTimeField(blank=True, null=True)
    PROGRESS_END_DATETIME = models.DateTimeField(blank=True, null=True)
    LOAD_STATE = models.CharField(max_length=30, default='model_not_found')
    DELETE_FLAG = models.BooleanField(default=False)
    ORIGINAL_DATA_SEQUENCE_FK1 = models.BigIntegerField()
    PREPROCESSED_DATA_SEQUENCE_FK2 = models.BigIntegerField(null=True)
    JOB_ID = models.CharField(max_length=100, blank=True)
    
    class Meta:
        managed = True
        db_table = 'MODEL'