#!/usr/bin/python
# -*- coding: utf-8 -*-

from pytz import common_timezones, country_timezones, country_names

from django.db import models
from django import forms
from django.forms.extras.widgets import Select

EMPTY_CHOICES = [('', '----------')]
#COUNTRY_CHOICES = [('', '----------')]
COUNTRY_CHOICES = [(cs, country_names[cs]) for cs in country_names]

class TimezoneConfig(models.Model):
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

    def save(self):
        # Salvar sempre na mesma linha do banco de dados
        self.id = 1
        super(TimezoneConfig, self).save()
    
    @classmethod
    def get_instance(cls):
        try:
            tzconf = cls.objects.get(pk=1)
        except cls.DoesNotExist:
            tzconf = cls()
        return tzconf
    
    @classmethod
    def timezone_configured(cls):
        """Returns True if timezone is configured, False otherwise."""
        return cls.objects.all().count() > 0

