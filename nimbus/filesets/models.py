from django.db import models

from nimbus.base.models import BaseModel

# Create your models here.

class FilePath(models.Model):
    path = models.FilePathField(max_length=255, null=False, unique=True)

    def __unicode__(self):
        return self.path



class FileSet(BaseModel):
    name = models.CharField(max_length=255, unique=True, null=False)
    files = models.ManyToManyField(FilePath)

    def __unicode__(self):
        return self.name
