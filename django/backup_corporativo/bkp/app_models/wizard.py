#!/usr/bin/python
# -*- coding: utf-8 -*-

import networkutils

from django.db import models
from django import forms
from django.http import QueryDict

from pytz import country_names

from backup_corporativo.bkp import customfields as cfields
from backup_corporativo.bkp.models import GlobalConfig, NetworkInterface, TimezoneConfig

EMPTY_CHOICES = [('', '----------')]
COUNTRY_CHOICES = [(cs, country_names[cs]) for cs in country_names]

class Wizard(models.Model):
    wizard_step = models.IntegerField(default = 0)
    wizard_lock = models.BooleanField("Lock", default = 0)
    # GlobalConfig
    globalconfig_name = models.CharField("Nome da Instância", max_length=64, null=True)
    director_port = models.IntegerField("Porta do Director", default='9101', null=True)
    storage_port = models.IntegerField("Porta do Storage", default='9103', null=True)
    total_backup_size = models.IntegerField("Tamanho Total do Backup (GB)", null=True)
    offsite_on = models.BooleanField("Offsite ativo?", default=False)        
    # NetwokrInterface
    interface_name = cfields.ModelSlugField( "Nome da Interface", max_length=30, null=True)
    interface_address = models.IPAddressField("Endereço IP", null=True)
    interface_netmask = models.IPAddressField("Máscara", null=True)
    interface_network = models.IPAddressField("Network", null=True)
    interface_broadcast = models.IPAddressField("Broadcast", null=True)
    interface_gateway = models.IPAddressField("Gateway Padrão", null=True)
    interface_dns1 = models.IPAddressField("Servidor DNS 1", null=True)
    interface_dns2 = models.IPAddressField("Servidor DNS 2", null=True)
    # TimeZone
    ntp_server = models.CharField("Servidor NTP", max_length=64, default="a.ntp.br")
    tz_country = models.CharField("País", max_length=32, blank=False, choices=COUNTRY_CHOICES)
    tz_area = models.CharField("Área", max_length=64, blank=False, choices=EMPTY_CHOICES, default=('', '----------'))

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
        
    @property
    def global_config(self):
        """ Gera um objeto do tipo GlobalConfig baseado
            nos atributos do Wizard 
        """
        gconfig_attrs = self.global_config_attributes()
        return GlobalConfig(**gconfig_attrs)

    @property
    def network_interface(self):
        """ Gera um objeto do tipo NetworkInterface baseado
            nos atributos do Wizard 
        """
        iface_attrs = self.network_interface_attributes()
        return NetworkInterface(**iface_attrs)
    
    @property
    def timezone_config(self):
        """ Gera um objeto do tipo TimezoneConfig baseado
            nos atributos do Wizard 
        """
        tconfig_attrs = self.timezone_config_attributes()
        return TimezoneConfig(**tconfig_attrs)


    def network_interface_querydict(self):
        """ Gera um QueryDict de um objeto NetworkInterface """
        iface_attrs = self.network_interface_attributes()
        return self.generate_querydict(iface_attrs)

    def global_config_querydict(self):
        """ Gera um QueryDict de um objeto GlobalConfig """
        gconfig_attrs = self.global_config_attributes()
        return self.generate_querydict(gconfig_attrs)
    
    def timezone_config_querydict(self):
        """ Gera um QueryDict de um objeto TimezoneConfig """
        tconfig_attrs = self.timezone_config_attributes()
        return self.generate_querydict(tconfig_attrs)

    def generate_querydict(self, attrs):
        """ Gera um QueryDict similar a um request.POST """
        query = ["%s=%s&" % (attr,attrs[attr]) for attr in attrs.keys()]
        return QueryDict("".join(query))


    def global_config_attributes(self):
        """ Lista de atributos relacionados a GlobalConfig """
        gconfig_attrs = [ 'globalconfig_name',
                        'director_port',
                        'storage_port',
                        'total_backup_size',
                        'offsite_on', ]
    
        return self.get_attributes(gconfig_attrs)

    def network_interface_attributes(self):
        """ Atributos relacionados a NetworkInterface """
        network_attrs = [ 'interface_name', 
                           'interface_address',
                           'interface_netmask',
                           'interface_network',
                           'interface_broadcast',
                           'interface_gateway',
                           'interface_dns1',
                           'interface_dns2' ]

        return self.get_attributes(network_attrs)
    
    def timezone_config_attributes(self):
        """ Lista de atributos relacionados a TimezoneConfig """
        tconfig_attrs = [ 'ntp_server',
                         'tz_country',
                         'tz_area', ]
    
        return self.get_attributes(tconfig_attrs)

    def get_attributes(self, target_attrs):
        """ Gera dicionário com atributos de wizard listados em
            target_attrs """
        all_attrs = self.__dict__

        return dict( (attr, all_attrs[attr]) \
                     for attr in all_attrs.keys() \
                     if attr in target_attrs)        

    def set_network_defaults(self):
        """ Colhe atributos do hardware da máquina """
        raw_iface = networkutils.get_interfaces()[0]
        self.interface_name = raw_iface.name
        self.interface_address = raw_iface.addr
        self.interface_netmask = raw_iface.netmask
        self.interface_broadcast = raw_iface.broadcast

    def save(self, *args, **kwargs):
        self.id = 1
        super(Wizard, self).save(*args, **kwargs)

    def __unicode__(self):
        return u"step: %s" % self.wizard_step

    @classmethod
    def get_instance(cls):
        try:
            wizard = cls.objects.get(pk=1)
        except cls.DoesNotExist:
            wizard = cls()
        return wizard
    
    @classmethod
    def get_wizard_lock(cls):
        if not cls.objects.all().count():
            return False
        elif cls.objects.all()[0].wizard_lock:
            return True
    
    def set_wizard_lock(self, value):
        self.wizard_lock = value
        self.save()
