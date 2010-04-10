from django.db import models
from backup_corporativo.bkp.models import NimbusUUID, Storage


class Device(models.Model):
    name = models.CharField(max_length=255)
    archive = models.FilePathField()
    storage = models.ForeignKey(Storage)

    def save(self, *args, **kwargs):
        NimbusUUID.generate_uuid_or_leave(self)
        super(Procedure, self).save(*args, **kwargs)


    def device_bacula_name(self):
        return "%s_device" % self.nimbus_uuid.uuid_hex
