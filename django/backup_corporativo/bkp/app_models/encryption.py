#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import string
import time

from django.core import serializers
from django.db import models
from django import forms

from keymanager import KeyManager

from backup_corporativo.bkp.models import TYPE_CHOICES, LEVEL_CHOICES, OS_CHOICES, DAYS_OF_THE_WEEK
from backup_corporativo.bkp import customfields as cfields
from backup_corporativo.bkp import utils
from backup_corporativo.bkp.app_models.nimbus_uuid import NimbusUUID
from backup_corporativo.bkp.app_models.computer import Computer


class Encryption(models.Model):
    nimbus_uuid = models.ForeignKey(NimbusUUID)
    computer = models.ForeignKey(Computer, unique=True)
    
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


    @classmethod
    def build_files(self, client_name):
        km = KeyManager()
        
        if not km.mounted:
            error = u"Cofre precisa estar aberto para criaçao de encriptaçao."
            raise Exception(error)
        rsa,cert = km.generate_and_save_keys_for_client(client_name)
        if not (rsa and cert):
            error = u"Nao foi possivel criar encriptaçao. Favor contactar suporte."
            raise Exception(error)
        return True

    def save(self):
        NimbusUUID.generate_uuid_or_leave(self)
        Encryption.build_files(self.computer.computer_name)
        super(Encryption, self).save()
        
    def __unicode__(self):
        return "Encriptação"