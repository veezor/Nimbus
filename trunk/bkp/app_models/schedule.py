#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.core import serializers
from django.db import models
from django import forms
from backup_corporativo.bkp.models import TYPE_CHOICES, LEVEL_CHOICES, OS_CHOICES, DAYS_OF_THE_WEEK
from backup_corporativo.bkp.models import Procedure
from backup_corporativo.bkp import customfields as cfields
from backup_corporativo.bkp import utils
import os, string, time


### Schedule ###
class Schedule(models.Model):
    procedure = models.ForeignKey(Procedure)
    type = models.CharField("Tipo",max_length=20,choices=TYPE_CHOICES)

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

    def build_backup(self, trigg):
        """Saves child objects in correct order."""
        trigg.schedule = self
        trigg.save()

    def __unicode__(self):
        if self.type == "Weekly":
            return "Semanal"
        elif self.type == "Monthly":
            return "Mensal"

    def edit_url(self):
        """Returns edit url."""
        return "schedule/%s/edit" % self.id

    def update_url(self):
        """Returns edit url."""
        return "schedule/%s/update" % self.id

    def delete_url(self):
        """Returns delete url."""
        return "schedule/%s/delete" % self.id

    # TODO: Otimizar codigo, remover if do schedule type (programaçao dinamica)
    def get_trigger(self):
        # Objetos precisam ser importados aqui, já que existe uma
        # dependência mútua entre Schedule e os Triggers.
        from backup_corporativo.bkp.models import WeeklyTrigger, MonthlyTrigger
        if self.type == 'Monthly':
            try:
                trigger = self.monthlytrigger_set.get()
                return trigger
            except MonthlyTrigger.DoesNotExist:
                return False
        elif self.type == 'Weekly':
            try:
                trigger = self.weeklytrigger_set.get()
                return trigger
            except WeeklyTrigger.DoesNotExist:
                return False
        else:
            raise Exception(
                "Erro de programação: tipo de agendamento inválido %s" % \
                    self.type)
        return "%strigger_set" % sched.type.lower()
