#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.core import serializers
from django.db import models
from django import forms
from backup_corporativo.bkp.models import TYPE_CHOICES, LEVEL_CHOICES, OS_CHOICES, DAYS_OF_THE_WEEK
from backup_corporativo.bkp import customfields as cfields
from backup_corporativo.bkp import utils
import os, string, time

### NimbusUUID ###
# UUID é gerado automaticamente utilizando o módulo uuid do Python
# (http://docs.python.org/library/uuid.html) que foi feito de acordo
# com a RFC 4122 (http://www.ietf.org/rfc/rfc4122.txt)
# Depois de criado, um uuid nunca deve ser alterado e isso serve para
# manter a integridade do sistema Nimbus.
class NimbusUUID(models.Model):
    # Constantes
    NIMBUS_BLANK = -1
    # Atributos
    uuid_hex = models.CharField(editable=False, max_length=32, unique=True, default=NIMBUS_BLANK)
    uuid_created_on = models.DateTimeField(editable=False)
    
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
        if self.uuid_hex == self.NIMBUS_BLANK:
            import uuid
            self.uuid_hex = uuid.uuid4().hex
            self.uuid_created_on = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            super(NimbusUUID, self).save()
        else: #TODO: Criar exceção do tipo Nimbus
            raise Exception("Erro de programação: objeto NimbusUUID não pode ser alterado.")

    def __unicode__(self):
        return "uuid_hex = %s" % self.uuid_hex
    
    #ClassMethods
    def build(cls):
        nuuid = cls()
        nuuid.save()
        return nuuid
    build = classmethod(build)

    # Esse método é chamado sempre que um objeto que possua
    # um NimbusUUID é alterado. UUID é gerado Apenas nos casos
    # em que o objeto ainda não possui um NimbusUUID
    def generate_uuid_or_leave(cls,object):
        try:
            object.nimbus_uuid
        except cls.DoesNotExist:
            object.nimbus_uuid = cls.build()
    generate_uuid_or_leave = classmethod(generate_uuid_or_leave)