#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.core import serializers
from django.db import models
from django import forms
from backup_corporativo.bkp.models import TYPE_CHOICES, LEVEL_CHOICES, OS_CHOICES, DAYS_OF_THE_WEEK
from backup_corporativo.bkp import customfields as cfields
from backup_corporativo.bkp import utils
import os, string, time


class NimbusLog(models.Model):
    entry_timestamp = models.DateTimeField(default='',blank=True)
    entry_category = models.CharField(max_length=30)
    entry_type = models.CharField(max_length=30)
    entry_content = models.TextField()

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
        self.entry_timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        try:
            from backup_corporativo.settings import LOG_LEVEL #TODO colocar LOG_LEVEL dentro de GlobalConfig
            if LOG_LEVEL == 0:          # Nenhum log
                pass
            elif LOG_LEVEL == 1:        # Somente em arquivo
                self.new_file_entry()
            elif LOG_LEVEL == 2:        # Somente em banco de dados
                super(NimbusLog, self).save()
            elif LOG_LEVEL == 3:        # Arquivo + banco de dados
                self.new_file_entry()
                super(NimbusLog, self).save()
            else:                       # LOG_LEVEL desconhecido
                raise Exception('Erro de configuração: LOG_LEVEL desconhecido.')
        except ImportError:
            pass

    def new_file_entry(self):
        nlog = NimbusLog.get_log_file()
        log_entry = "%s [%s] - %s: %s" % (self.entry_timestamp, self.entry_category, self.entry_type, self.entry_content)
        nlog.write(str(log_entry).encode("string-escape"))
        nlog.write("\n")
        nlog.close()

    # ClassMethods
    def get_log_file(cls):
        return utils.prepare_to_write('log_geral','custom/logs/',mod='a')
    get_log_file = classmethod(get_log_file)
    
    def notice(cls, category, type, content):
        n1 = NimbusLog()
        n1.entry_category = category
        n1.entry_type = type
        n1.entry_content = content
        n1.save()
    notice = classmethod(notice)