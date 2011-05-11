
from django.db import models
from nimbus.base.models import SingletonBaseModel

MANAGED="MANAGED"
STANDALONE="STANDALONE"
REMOTE_STORAGE_STATES = ( MANAGED, STANDALONE )
REMOTE_STORAGE_STATES_CHOICES = ( (x,x) for x in REMOTE_STORAGE_STATES )


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
