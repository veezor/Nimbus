from django.contrib import admin
from gateway.nimbusgate.models import OperationLog, UserBucket, Operation

admin.site.register(OperationLog)
admin.site.register(UserBucket)
admin.site.register(Operation)
