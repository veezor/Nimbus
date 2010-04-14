#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.db import models
from backup_corporativo.bkp import utils

from backup_corporativo.bkp.app_models.nimbus_uuid import NimbusUUID
from backup_corporativo.bkp.app_models.global_config import GlobalConfig

### Storage ###
class Storage(models.Model):
    # Constantes
    NIMBUS_BLANK = -1
    # Atributos
    nimbus_uuid = models.ForeignKey(NimbusUUID, default=NIMBUS_BLANK)
    storage_name = models.CharField("Nome", max_length=50)
    storage_ip = models.IPAddressField("Endereço IP", default="127.0.0.1")
    storage_port = models.IntegerField("Porta do Storage", default='9103')
    storage_password = models.CharField(max_length=50, default=NIMBUS_BLANK)
    storage_description = models.CharField(
        "Descrição", max_length=100, blank=True)

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

    def save(self, *args, **kwargs):
        if self.storage_password == self.NIMBUS_BLANK:
            self.storage_password = utils.random_password()

        NimbusUUID.generate_uuid_or_leave(self)
        super(Storage, self).save(*args, **kwargs)

    def storage_bacula_name(self):
        return "%s_storage" % self.nimbus_uuid.uuid_hex

    def __unicode__(self):
        return "%s (%s:%s)" % (
            self.storage_name,
            self.storage_ip,
            self.storage_port)

    @classmethod
    def get_instance(cls):
        try:
            sto = cls.objects.get(pk=1)
        except cls.DoesNotExist:
            sto = cls()
        return sto
