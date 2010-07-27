from django.db import models

from nimbus.base.models import BaseModel
from nimbus.procedure.models import Procedure
# Create your models here.

class Pool(BaseModel):
    name = models.CharField(max_length=255)
    procedure = models.ForeignKey(Procedure, blank=False, null=False)
    pool_size = models.FloatField(blank=False, null=False)
    retention_time = models.IntegerField(blank=False, null=False, default=30)
