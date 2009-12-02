#!/usr/bin/python
# -*- coding: utf-8 -*-


from django.core import serializers
from django.db import models
from django import forms
from backup_corporativo.bkp.models import TYPE_CHOICES, LEVEL_CHOICES, OS_CHOICES, DAYS_OF_THE_WEEK
from backup_corporativo.bkp import customfields as cfields
from backup_corporativo.bkp import utils
import os, string, time

from backup_corporativo.bkp.app_models.nimbus_uuid import NimbusUUID


### GlobalConfig ###
class GlobalConfig(models.Model):
    # Constantes
    NIMBUS_BLANK = -1
    # Atributos
    nimbus_uuid = models.ForeignKey(NimbusUUID)
    globalconfig_name = models.CharField(
        "Nome da Instância",
        max_length=50)
    director_password = models.CharField(
        max_length=50,
        default=NIMBUS_BLANK)
    director_port = models.IntegerField(
        "Porta do Director",
        default='9101')
    storage_port = models.IntegerField(
        "Porta do Storage",
        default='9103')
    offsite_on = models.BooleanField(
        "Offsite ativo?",
        default=False)
    offsite_hour = models.TimeField("Horário", default="00:00:00")

    # Classe Meta é necessária para resolver um problema gerado quando se
    # declara um model fora do arquivo models.py. Foi utilizada uma solução
    # temporária que aparentemente funciona normalmente. 
    # Para mais informações sobre esse hack, acessar ticket:
    # http://code.djangoproject.com/ticket/4470
    # NOTA: No momento em que esse código foi escrito, o Django estava
    # na versão "Django-1.0.2-final" e uma alteração no core do Django
    # estava sendo discutida em paralelo, mas o ticket ainda encontrava-se em
    # aberto e portanto ainda sem solução definitiva.
    # Caso um dia a aplicação venha a quebrar nesse trecho do código por conta
    # de uma atualização para uma versão do Django superior a 1.0.2,
    # vale a pena verificar se alguma alteração foi realmente realizada
    # nessa nova versão do Django.
    # Para mais informações sobre essa correção, acessar ticket:
    # http://code.djangoproject.com/ticket/3591
    class Meta:
        app_label = 'bkp'    

    #TODO: atualizar porta do storage de acordo com campo do GlobalConfig!!
    def save(self):
        if self.director_password == self.NIMBUS_BLANK:
            self.director_password = utils.random_password()
            # NetworkInterface.networkconfig.save()
        NimbusUUID.generate_uuid_or_leave(self)
        # O import do Storage deve ser dentro da função porque existe uma
        # dependência mútua entre Storage e GlobalConfig. Assim ambos não
        # podem um referenciar ao outro no escopo geral do arquivo ao
        # mesmo tempo.
        from backup_corporativo.bkp.app_models.storage import Storage
        Storage.update_default_storage(self.storage_port)
        # Use sempre o mesmo id para armazenar o Storage Local
        self.id = 1
        super(GlobalConfig, self).save()

    def director_bacula_name(self):
        return "%s_director" % self.nimbus_uuid.uuid_hex

    def storage_bacula_name(self):
        return "%s_storage" % self.nimbus_uuid.uuid_hex

    def system_configured(cls):
        """Returns True if system is configured, False otherwise."""
        return cls.objects.all().count() > 0
    system_configured = classmethod(system_configured)
    
    def bacula_database_name(cls):
        from backup_corporativo.settings import BACULA_DATABASE_NAME
        return BACULA_DATABASE_NAME
    bacula_database_name = classmethod(bacula_database_name)

    def bacula_database_user(cls):
        from backup_corporativo.settings import BACULA_DATABASE_USER
        return BACULA_DATABASE_USER
    bacula_database_user = classmethod(bacula_database_user)
    
    def bacula_database_password(cls):
        from backup_corporativo.settings import BACULA_DATABASE_PASSWORD
        return BACULA_DATABASE_PASSWORD
    bacula_database_password = classmethod(bacula_database_password)

    def admin_mail(cls):
        return "nimbus@linconet.com.br"
    admin_mail = classmethod(admin_mail)
