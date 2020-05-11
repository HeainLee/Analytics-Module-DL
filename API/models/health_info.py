######################[헬스정보를 디비에 저장]#######################
from django.db import models


class HealthInfo(models.Model):
    identifier = models.CharField(primary_key=True, max_length=20)
    HEALTH_INFO = models.TextField(blank=True)

    class Meta:
        managed = True
        db_table = 'HEALTH_INFO'