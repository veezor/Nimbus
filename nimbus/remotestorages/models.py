


from django.db import models
from django.conf import settings


import systeminfo

from nimbus.base.models import SingletonBaseModel
from nimbus.storages.models import Storage
from nimbus.remotestorages import notifier


MANAGED="MANAGED"
STANDALONE="STANDALONE"
REMOTE_STORAGE_STATES = ( MANAGED, STANDALONE )
REMOTE_STORAGE_STATES_CHOICES = ( (x,x) for x in REMOTE_STORAGE_STATES )


OK="OK"
WARNNING="WARNNING"
CRITICAL="CRITICAL"
REMOTE_STORAGE_STATUS = ( OK, WARNNING, CRITICAL )
REMOTE_STORAGE_STATUS_CHOICES = ( (x,x) for x in REMOTE_STORAGE_STATUS )




class RemoteStorageStatus(models.Model):
    storage = models.ForeignKey(Storage, null=False, unique=True)
    state = models.CharField(max_length=255, default=STANDALONE,
                             choices=REMOTE_STORAGE_STATES_CHOICES,
                             blank=False, null=False, unique=False)

    status = models.CharField(max_length=255, default=OK,
                             choices=REMOTE_STORAGE_STATUS_CHOICES,
                             blank=False, null=False, unique=False)

    disk_usage = models.IntegerField(null=False,unique=False)
    online = models.BooleanField(default=False, null=False,unique=False)



class RemoteStorageConf(SingletonBaseModel):
    disk_warning_threshold = models.IntegerField(default=-1, blank=False, null=False, unique=False)
    disk_critical_threshold = models.IntegerField(default=-1, blank=False, null=False, unique=False)
    state = models.CharField(max_length=255, default=MANAGED, choices=REMOTE_STORAGE_STATES_CHOICES, 
                             blank=False, null=False, unique=False)

    def set_managed_mode(self):
        self.state = MANAGED

    def set_standalone_mode(self):
        self.state = STANDALONE

    def managed_mode(self):
        return self.state == MANAGED

    def standalone_mode(self):
        return self.state == STANDALONE



def send_disk_usage_alert():
    disk_info = systeminfo.DiskInfo(path=settings.DEFAULT_BACULA_ARCHIVE)
    usage = int(disk_info.get_usage())

    config = RemoteStorageConf.get_instance()
    if usage >= config.disk_critical_threshold:
        notifier.DiskCriticalNotifier().notify()
        return

    if usage >= config.disk_warning_threshold:
        notifier.DiskWarnningNotifier().notify()

