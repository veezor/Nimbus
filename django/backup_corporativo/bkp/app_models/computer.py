#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import string
import time

from django.core import serializers
from django.db import models
from django import forms

from backup_corporativo.bkp.sql_queries import CLIENT_RUNNING_JOBS_RAW_QUERY, CLIENT_STATUS_RAW_QUERY, CLIENT_LAST_JOBS_RAW_QUERY, CLIENT_ID_RAW_QUERY
from backup_corporativo.bkp.models import TYPE_CHOICES, LEVEL_CHOICES, OS_CHOICES, DAYS_OF_THE_WEEK
from backup_corporativo.bkp import customfields as cfields
from backup_corporativo.bkp import utils
from backup_corporativo.bkp.bacula import Bacula
from backup_corporativo.bkp.app_models.nimbus_uuid import NimbusUUID
from backup_corporativo.bkp.app_models.global_config import GlobalConfig

import pybacula
pybacula.test()
bacula = Bacula()


class ComputerLimitExceeded(Exception):
    pass

### Computer ###
class Computer(models.Model):
    # Constants
    DEFAULT_LOCATION="/tmp/bacula-restore"
    NIMBUS_BLANK = -1
    NIMBUS_ERROR = 0
    # Attributes
    nimbus_uuid = models.ForeignKey(NimbusUUID)
    computer_name = models.CharField(
        "Nome",
        max_length=50,
        unique=True)
    computer_ip = models.IPAddressField("Endereço IP")
    computer_so = models.CharField(
        "Sistema Operacional",
        max_length=50,
        choices=OS_CHOICES)
    computer_encryption = models.BooleanField(
        "Encriptar Dados?",
        default=False)
    computer_description = models.TextField(
        "Descrição",
        max_length=100,
        blank=True)
    computer_password = models.CharField(
        "Password",
        max_length=25,
        editable=False,
        default=NIMBUS_BLANK)
    computer_bacula_id = models.IntegerField(
        "Bacula ID",
        default=NIMBUS_BLANK)

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
        if Computer.objects.count() > 14:
            raise ComputerLimitExceeded
        if self.computer_password == self.NIMBUS_BLANK:
            self.computer_password = utils.random_password()
        uuid = NimbusUUID()
        uuid.save()
        self.nimbus_uuid = uuid
        #NimbusUUID.generate_uuid_or_leave(self)
        super(Computer, self).save()
        if self.computer_bacula_id == self.NIMBUS_BLANK:
            self.__update_bacula_id()

    def computer_bacula_name(self):
        return "%s_client" % self.nimbus_uuid.uuid_hex

    #TODO: Refatorar código
    def get_status(self):
        """
        Atualiza status do computador baseado no 
       status de término do último Job executado
        """
        status_query = CLIENT_STATUS_RAW_QUERY % {
            'client_name':self.computer_bacula_name(),}
        cursor = bacula.baculadb.execute(status_query)
        result = cursor.fetchone()
        status = result and result[0] or ''

        if status == 'T':
            return 'Ativo'
        elif status == 'E':
            return 'Erro'
        else:
            return 'Desconhecido'

    def computer_encryption_friendly(self):
        return self.computer_encryption and 'Ativada' or 'Desativada'

    def computer_so_friendly(self):
        if self.computer_so == 'WIN':
            return 'Windows'
        elif self.computer_so == 'UNIX':
            return 'Unix'
        else:
            return 'Desconhecido'

    # TODO: refatorar código e separar em várias funções
    def dump_filedaemon_config(self):
        """Gera arquivo de configuraçãodo cliente bacula-sd.conf."""
        import time
        
        fd_dict =   {
                    'Name': self.computer_name,
                    #TODO: tratar porta do cliente
                    'FDport':'9102',
                    'Maximum Concurrent Jobs':'5',}
                    
        if self.computer_encryption:
            if self.computer_so == 'UNIX':
                fd_dict.update({
                    'PKI Signatures':'Yes',
                    'PKI Encryption':'Yes',
                    'PKI Keypair':'''"/etc/bacula/%s"''' % \
                        self.computer_pem(),
                    'PKI Master Key':'''"/etc/bacula/master.cert"''',})
            elif self.computer_so == 'WIN':
                fd_dict.update({
                    'PKI Signatures':'Yes',
                    'PKI Encryption':'Yes',
                    'PKI Keypair':'''"C:\\\\Nimbus\\\\%s"''' % \
                        self.computer_pem(),
                    'PKI Master Key':'''"C:\\\\Nimbus\\\\master.cert"''',})
            
        if self.computer_so == 'UNIX':
            fd_dict.update({
                'WorkingDirectory':'/var/bacula/working ',
                'Pid Directory':'/var/run ',})
        elif self.computer_so == 'WIN':
            fd_dict.update({
                'WorkingDirectory':'''"C:\\\\Nimbus"''',
                'Pid Directory':'''"C:\\\\Nimbus"''',})
        gconf = GlobalConfig.objects.get(pk=1)
        dir_dict =  {
            'Name':gconf.director_bacula_name(),
            'Password':'''"%s"''' % (self.computer_password),}
        msg_dict =  {
            'Name':'Standard',
            'director':'%s = all, !skipped, !restored' % \
                gconf.director_bacula_name(),}
        dump = []
    
        dump.append("#\n")
        # TODO: adicionar version stamp aqui
        dump.append("# Generated by Nimbus %s\n" % \
            time.strftime("%d-%m-%Y %H:%M:%S", time.localtime()))
        dump.append("#\n")
        dump.append("FileDaemon {\n")
        for k in fd_dict.keys():
            dump.append('''\t%(key)s = %(value)s\n''' % {
                'key':k,'value':fd_dict[k]})
        dump.append("}\n\n")
        dump.append("Director {\n")
        for k in dir_dict.keys():
            dump.append('''\t%(key)s = %(value)s\n''' % {
                'key':k,'value':dir_dict[k]})
        dump.append("}\n\n")
        dump.append("Messages {\n")
        for k in msg_dict.keys():
            dump.append('''\t%(key)s = %(value)s\n''' % {
                'key':k,'value':msg_dict[k]})
        dump.append("}\n\n")
        
        return dump

    def build_backup(self, proc, fset, sched, wtrigg):
        """Saves child objects in correct order."""
        proc.computer = self
        proc.save()
        fset.procedure = sched.procedure = proc
        fset.save()
        sched.save()
        wtrigg.schedule = sched
        wtrigg.save()

    def running_jobs(self):
        running_jobs_query = CLIENT_RUNNING_JOBS_RAW_QUERY % {
            'client_name':self.computer_bacula_name(),}
        running_jobs_cursor = bacula.baculadb.execute(running_jobs_query)
        return utils.dictfetch(running_jobs_cursor)

    def last_jobs(self):
        last_jobs_query = CLIENT_LAST_JOBS_RAW_QUERY % {
            'client_name':self.computer_bacula_name(),}
        last_jobs_cursor = bacula.baculadb.execute(last_jobs_query)
        return utils.dictfetch(last_jobs_cursor)

    def run_test_job(self):
        """Sends an empty job running requisition to bacula for this computer"""
        from backup_corporativo.bkp.bacula import Bacula;
        Bacula.run_backup(
            JobName='Teste Conectividade',
            client_name=self.computer_bacula_name())

    def absolute_url(self):
        """Returns absolute url."""
        return "computer/%s" % self.id

    def view_url(self):
        """Returns absolute url."""
        return "computer/%s" % self.id

    def edit_url(self):
        """Returns absolute url."""
        return "computer/%s/edit" % self.id

    def delete_url(self):
        """Returns delete url."""
        return "computer/%s/delete" % self.id

    def computer_config_url(self):
        return "computer/%s/config/" % self.id 
    
    def computer_dump_config_url(self):
        """Returns config dump url."""
        return "computer/%s/config/dump" % self.id
   
    def run_test_url(self):
        """Returns run test url."""
        return "computer/%s/test" % self.id

    def __update_bacula_id(self):
        """Queries bacula database for client id"""
        cliend_id_query = CLIENT_ID_RAW_QUERY % {
            'client_name':self.computer_bacula_name()}
        cursor = bacula.baculadb.cursor()
        cursor.execute(cliend_id_query)
        client_id = cursor.fetchone()
        self.computer_bacula_id = \
            client_id and client_id[0] or self.NIMBUS_ERROR
        self.save()

    def __unicode__(self):
        return "%s (%s)" % (self.computer_name, self.computer_ip)
