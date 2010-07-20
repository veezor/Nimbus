#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import time
import string

from django.core import serializers
from django.db import models
from django import forms

from backup_corporativo.bkp import customfields as cfields
from backup_corporativo.bkp import utils


### Constants ###
TYPE_CHOICES = (
    ('Weekly', 'Semanal'),
    ('Monthly', 'Mensal'),
)

LEVEL_CHOICES = (
    ('Full', 'Completo'),
    ('Incremental', 'Incremental'),
)

OS_CHOICES = (
    ('WIN', 'Windows'),
    ('UNIX', 'Unix'),
)


DAYS_OF_THE_WEEK = {
    'sunday':'Domingo','monday':'Segunda','tuesday':'Terça',
    'wednesday':'Quarta','thursday':'Quinta','friday':'Sexta',
    'saturday':'Sábado',
}



from backup_corporativo.bkp.app_models.nimbus_uuid import NimbusUUID
from backup_corporativo.bkp.app_models.encryption import Encryption

from backup_corporativo.bkp.app_models.global_config import GlobalConfig
from backup_corporativo.bkp.app_models.network_interface import NetworkInterface
from backup_corporativo.bkp.app_models.timezone_config import TimezoneConfig

from backup_corporativo.bkp.app_models.storage import Storage

from backup_corporativo.bkp.app_models.computer import Computer
from backup_corporativo.bkp.app_models.computeraddrequest import ComputerAddRequest
from backup_corporativo.bkp.app_models.procedure import Procedure
from backup_corporativo.bkp.app_models.schedule import Schedule
from backup_corporativo.bkp.app_models.weekly_trigger import WeeklyTrigger
from backup_corporativo.bkp.app_models.monthly_trigger import MonthlyTrigger
from backup_corporativo.bkp.app_models.pool import Pool
from backup_corporativo.bkp.app_models.file_set import FileSet
from backup_corporativo.bkp.app_models.device import Device


from backup_corporativo.bkp.app_models.header_bkp import HeaderBkp

from backup_corporativo.bkp.app_models.wizard import Wizard


from backup_corporativo.bkp.app_models.offsite import (UploadedVolume, 
                                                       Volume,
                                                       DownloadedVolume,
                                                       DownloadRequest,
                                                       UploadRequest )

###
###   Signals
###
import backup_corporativo.bkp.signals

#
# Atenção:
#
# É preciso remover variável de ambiente
# para que o Django não interfira no 
# funcionamento do timezone
# que normalmente é estático e configurado
# no "settings.py".
#
# Este código deve ser executado apenas uma vez.
if 'TZ' in os.environ:
    del(os.environ['TZ'])
