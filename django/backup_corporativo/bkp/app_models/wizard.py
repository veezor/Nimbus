#!/usr/bin/python
# -*- coding: utf-8 -*-

import networkutils

from django.db import models
from django import forms
from django.http import QueryDict

from pytz import country_names

from backup_corporativo.bkp import customfields as cfields
from backup_corporativo.bkp.models import GlobalConfig, NetworkInterface, TimezoneConfig


class Wizard(models.Model):
    state = models.IntegerField(default = 0)
    completed = models.BooleanField(default = False)
    config = models.ForeignKey(GlobalConfig, null=True)
    network = models.ForeignKey(NetworkInterface, null=True)
    timezone = models.ForeignKey(TimezoneConfig, null=True)

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
        
    def set_network_defaults(self):
        """ Colhe atributos do hardware da máquina """

        interface = NetworkInterface()
        self.network = interface


        raw_iface = networkutils.get_interfaces()[0]
        self.network.interface_name = raw_iface.name
        self.network.interface_address = raw_iface.addr
        self.network.interface_netmask = raw_iface.netmask
        self.network.interface_broadcast = raw_iface.broadcast

        self.save()

    def save(self, *args, **kwargs):
        self.id = 1
        super(Wizard, self).save(*args, **kwargs)

    def __unicode__(self):
        return u"Wizard(state=%d)" % self.state

    @classmethod
    def get_instance(cls):
        try:
            wizard = cls.objects.get(pk=1)
        except cls.DoesNotExist:
            wizard = cls()
        return wizard
    
    @classmethod
    def has_completed(cls):
        return cls.get_instance().completed
    
    def finish(self):
        self.completed = True
        self.save()
