from django.db import models
from django.contrib.auth.models import User
from datetime import datetime

# Create your models here.


OPERATION_CHOICES = (
        ( 'PUT' , 'PUT' ),
        ( 'GET' , 'GET' ),
        ( 'LIST' , 'LIST' ),
        ( 'DELETE' , 'DELETE' )
)


class Operation(models.Model):
    name = models.CharField(max_length=50, choices = OPERATION_CHOICES)

    def __unicode__(self):
        return "Operation(%s)" % self.name

class OperationLog(models.Model):
    datetime = models.DateTimeField(default=datetime.now())
    user = models.ForeignKey(User)
    operation = models.ForeignKey(Operation)
    path = models.FilePathField(blank=True)
    datalen = models.IntegerField(blank=True)
    httpcode = models.IntegerField(default=0)

class UserBucket(models.Model):
    user = models.ForeignKey(User)
    name = models.CharField(max_length=50)

    def __unicode__(self):
        return u"User(%s)-Bucket(%s)" % (self.user.username, self.name)


