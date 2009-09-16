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

### Storage ###
class Storage(models.Model):
    # Constantes
    NIMBUS_BLANK = -1
    # Atributos
    nimbus_uuid = models.ForeignKey(NimbusUUID, default=NIMBUS_BLANK)
    storage_name = models.CharField("Nome", max_length=50, unique=True)
    storage_ip = models.IPAddressField("Endereço IP")
    storage_port = models.IntegerField("Porta do Storage", default='9103')
    storage_password = models.CharField(max_length=50, default=NIMBUS_BLANK)
    storage_description = models.CharField("Descrição", max_length=100, blank=True)

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

    def save(self):
        if self.storage_password == self.NIMBUS_BLANK:
            self.storage_password = utils.random_password()
        NimbusUUID.generate_uuid_or_leave(self)
        super(Storage, self).save()

    def storage_bacula_name(self):
        return "%s_storage" % (self.nimbus_uuid.uuid_hex)


    def delete(self):
        if self.storage_name == 'Storage Local': # TODO: criar exceção do tipo Nimbus
            raise Exception('Erro de Programação: Storage Local não pode ser removido.') 
        else:
            super(Storage, self).delete()

    def absolute_url(self):
        """Returns absolute url."""
        return "storage/%s" % (self.id)

    def view_url(self):
        """Returns absolute url."""
        return "storage/%s" % (self.id)

    def edit_url(self):
        """Returns absolute url."""
        return "storage/%s/edit" % (self.id)

    def delete_url(self):
        """Returns delete url."""
        return "storage/%s/delete" % (self.id)

    def __unicode__(self):
        return "%s (%s:%s)" % (self.storage_name, self.storage_ip, self.storage_port)

    # ClassMethods
    def default_storage(cls):
        return cls.objects.get(storage_name='Storage Local')
    default_storage = classmethod(default_storage)

    # Esse método é chamado toda vez que GlobalConfig é
    # modificado. Assim, a única forma de alterar as configurações
    # do Storage Local é através de GlobalConfig.
    def update_default_storage(cls, server_ip, storage_port):
        try:
            sto = cls.default_storage()
        except Storage.DoesNotExist:
            sto = cls()
        sto.storage_name = 'Storage Local'
        sto.storage_description = 'Storage Local do Nimbus'
        sto.storage_ip = server_ip
        sto.storage_port = storage_port
        sto.save()
    update_default_storage = classmethod(update_default_storage)
