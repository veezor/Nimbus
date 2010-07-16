from django.db import models

from backup_corporativo.bkp.models import OS_CHOICES 

class ComputerAddRequest(models.Model):
    name = models.CharField(max_length=50, default="Ausente")
    ip = models.IPAddressField(unique=True,null=False)
    operation_system = models.CharField(max_length=50, choices=OS_CHOICES,null=False)


    def __unicode__(self):
        return u"ComputerRequest(name=%s,ip=%s,os=%s)" % ( self.name,
                                                           self.ip,
                                                           self.operation_system )
                                                            

    class Meta:
        app_label = 'bkp'
