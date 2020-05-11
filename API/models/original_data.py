######################[데이터 원본(학습데이터) 관리]#######################
from django.db import models

class OriginalData(models.Model):
    ORIGINAL_DATA_SEQUENCE_PK=models.BigAutoField(primary_key=True, unique=True)
    NAME=models.CharField(max_length=100)
    FILEPATH=models.CharField(max_length=300)
    FILENAME=models.CharField(max_length=100)
    EXTENSION=models.CharField(max_length=30)
    CREATE_DATETIME=models.DateTimeField(auto_now_add=True)
    COLUMNS=models.TextField()
    STATISTICS=models.TextField()
    SAMPLE_DATA=models.TextField()
    AMOUNT=models.BigIntegerField()
    DELETE_FLAG=models.BooleanField(default=False)

    class Meta:
        managed = True
        db_table = 'ORIGINAL_DATA'