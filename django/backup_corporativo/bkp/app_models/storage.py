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
from backup_corporativo.bkp.app_models.global_config import GlobalConfig

### Storage ###
class Storage(models.Model):
    # Constantes
    NIMBUS_BLANK = -1
    # Atributos
    nimbus_uuid = models.ForeignKey(NimbusUUID, default=NIMBUS_BLANK)
    storage_name = models.CharField("Nome", max_length=50, unique=True)
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

    def save(self):
        if self.storage_password == self.NIMBUS_BLANK:
            self.storage_password = utils.random_password()
        NimbusUUID.generate_uuid_or_leave(self)
        self.id = 1
        super(Storage, self).save()

    def storage_bacula_name(self):
        return "StorageLocal"


    def delete(self):
        # TODO: criar exceção do tipo Nimbus
        if self.storage_name == 'StorageLocal': 
            raise Exception(
                'Erro de Programação: Storage Local não pode ser removido.') 
        else:
            super(Storage, self).delete()

    def dump_storagedaemon_config(self):
        gconf = GlobalConfig.objects.get(pk=1)
        sto_dict = {
            'Name':self.storage_bacula_name,
            'SDPort':self.storage_port,
            'WorkingDirectory':'"/var/bacula/working"',
            'Pid Directory':'"/var/run"',
            'Maximum Concurrent Jobs':'20'}
        dir_dict = {
            'Name':gconf.director_bacula_name(),
            'Password':'"%s"' % self.storage_password}
        dev_dict = {
            'Name':"FileStorage",
            'Media Type':'File',
            'Archive Device':'/var/backup',
            'LabelMedia':'yes', 
            'Random Access':'yes',
            'AutomaticMount':'yes',
            'RemovableMedia':'no',
            'AlwaysOpen':'no'}
        msg_dict = {
            'Name':"Standard",
            'Director':'%s = all' % gconf.director_bacula_name()}
        
        dump = []
    
        dump.append("Storage {\n")
        for k in sto_dict.keys():
            dump.append('''\t%(key)s = %(value)s\n''' % {
                'key':k,'value':sto_dict[k]})
        dump.append("}\n\n")
    
        dump.append("Director {\n")
        for k in dir_dict.keys():
            dump.append('''\t%(key)s = %(value)s\n''' % {
                'key':k,'value':dir_dict[k]})
        dump.append("}\n\n")
        
        dump.append("Device {\n")
        for k in dev_dict.keys():
            dump.append('''\t%(key)s = %(value)s\n''' % {
                'key':k,'value':dev_dict[k]})
        dump.append("}\n\n")
        
        dump.append("Messages {\n")
        for k in msg_dict.keys():
            dump.append('''\t%(key)s = %(value)s\n''' % {
                'key':k,'value':msg_dict[k]})
        dump.append("}\n\n")
        
        return dump

    def absolute_url(self):
        """Returns absolute url."""
        return "storage/%s" % self.id

    def view_url(self):
        """Returns absolute url."""
        return "storage/%s" % self.id

    def edit_url(self):
        """Returns absolute url."""
        return "storage/%s/edit" % self.id

    def delete_url(self):
        """Returns delete url."""
        return "storage/%s/delete" % self.id

    def storage_config_url(self):
        return "storage/%s/config/" % self.id
    
    def storage_dump_config_url(self):
        return "storage/%s/config/dump" % self.id

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
