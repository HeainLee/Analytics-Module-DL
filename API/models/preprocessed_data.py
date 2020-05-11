######################[전처리된 데이터 관리]#######################
from django.db import models

class PreprocessedData(models.Model):
    PREPROCESSED_DATA_SEQUENCE_PK = models.BigAutoField(primary_key=True, unique=True)
    COMMAND = models.TextField()
    FILEPATH = models.CharField(max_length=300, blank=True)
    FILENAME = models.CharField(max_length=100, blank=True)
    SUMMARY = models.TextField(blank=True)
    CREATE_DATETIME = models.DateTimeField(auto_now_add=True)
    PROGRESS_STATE = models.CharField(max_length=30, default='standby')
    PROGRESS_START_DATETIME = models.DateTimeField(blank=True, null=True)
    PROGRESS_END_DATETIME = models.DateTimeField(blank=True, null=True)
    COLUMNS=models.TextField()
    STATISTICS=models.TextField()
    SAMPLE_DATA=models.TextField()
    AMOUNT=models.BigIntegerField()
    DELETE_FLAG = models.BooleanField(default=False)
    ORIGINAL_DATA_SEQUENCE_FK1 = models.BigIntegerField()

    class Meta:
        managed = True
        db_table = 'PREPROCESSED_DATA'