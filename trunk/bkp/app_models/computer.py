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


### Computer ###
class Computer(models.Model):
    # Constants
    DEFAULT_LOCATION="/tmp/bacula-restore"
    NIMBUS_BLANK = -1
    NIMBUS_ERROR = 0
    # Attributes
    nimbus_uuid = models.ForeignKey(NimbusUUID)
    computer_name = models.CharField("Nome",max_length=50,unique=True)
    computer_ip = models.IPAddressField("Endereço IP")
    computer_so = models.CharField("Sistema Operacional",max_length=50,choices=OS_CHOICES)
    computer_encryption = models.BooleanField("Encriptar Dados?",default=False)
    computer_description = models.TextField("Descrição",max_length=100, blank=True)
    computer_password = models.CharField("Password",max_length=25, editable=False, default=NIMBUS_BLANK)
    computer_bacula_id = models.IntegerField("Bacula ID", default=NIMBUS_BLANK)

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
        if self.computer_password == self.NIMBUS_BLANK:
            self.computer_password = utils.random_password()
        NimbusUUID.generate_uuid_or_leave(self)
        super(Computer, self).save()
        if self.computer_bacula_id == self.NIMBUS_BLANK:
            self.__update_bacula_id()

    def computer_bacula_name(self):
        return "%s_client" % (self.nimbus_uuid.uuid_hex)

    #TODO: Refatorar código
    def get_status(self):
        """
        Atualiza status do computador baseado no 
        status de término do último Job executado
        """
        from backup_corporativo.bkp.bacula import BaculaDatabase
        from backup_corporativo.bkp.sql_queries import CLIENT_STATUS_RAW_QUERY
        status_query = CLIENT_STATUS_RAW_QUERY % {'client_name':self.computer_bacula_name(),}
        cursor = BaculaDatabase.execute(status_query)
        result = cursor.fetchone()
        status = result and result[0] or ''

        if status == 'T':
            return 'Ativo'
        elif status == 'E':
            return 'Erro'
        else:
            return 'Desconhecido'

    def computer_rsa_key_path(self):
        """Retorna o caminho completo para o arquivo de chave rsa."""
        return utils.absolute_file_path("%s.key" % self.computer_name,"custom/crypt/")

    def computer_certificate_path(self):
        """Retorna caminho completo para o arquivo de certificado."""
        return utils.absolute_file_path("%s.cert" % self.computer_name,"custom/crypt/")

    def computer_pem_path(self):
        """Retorna caminho completo para o arquivo PEM."""
        return utils.absolute_file_path("%s.pem" % self.computer_name,"custom/crypt/")

    def __generate_rsa_key(self):
        from backup_corporativo.bkp.crypt_utils import GENERATE_RSA_KEY_RAW_CMD
        utils.create_or_leave(utils.absolute_dir_path('custom/crypt'))
        cmd = GENERATE_RSA_KEY_RAW_CMD % {'out':self.computer_rsa_key_path()}
        os.popen(cmd).read()
        

    def __generate_certificate(self):
        from backup_corporativo.bkp.utils import CERTIFICATE_CONFIG_PATH
        from backup_corporativo.bkp.crypt_utils import GENERATE_CERT_RAW_CMD
        utils.create_or_leave(utils.absolute_dir_path('custom/crypt'))
        rsa_key_path = self.computer_rsa_key_path()
        if not os.path.isfile(rsa_key_path):
            raise Exception(u"Não foi possível encontrar Chave RSA. Tentou-se: %s" % rsa_key_path)
        cmd = GENERATE_CERT_RAW_CMD % {'key_path':rsa_key_path, 'conf':CERTIFICATE_CONFIG_PATH, 'out':self.computer_certificate_path()}
        os.popen(cmd).read()

    def dump_rsa_key(self):
        self.__generate_rsa_key()
        f = open(self.computer_rsa_key_path())
        dump = []
        for line in f:
            dump.append(str(line))
            
        return '\n'.join(dump)	
        

    def dump_certificate(self):
        self.__generate_certificate()
        f = open(self.computer_certificate_path())
        dump = []
        for line in f:
            dump.append(str(line))
            
        return '\n'.join(dump)	

    
    #TODO: verificar se o PEM que foi gerado é válido.
    def dump_pem(self):
        """
        Gera PEM do computador
        PEM consiste na concatenação da chave
        e do certificado no mesmo arquivo.
        """
        from backup_corporativo.bkp.crypt_utils import GET_PEM_RAW_CMD
        rsa_key_path = self.computer_rsa_key_path()
        certificate_path = self.computer_certificate_path()
        if not os.path.isfile(rsa_key_path):
            raise Exception(u"Não foi possível encontrar Chave RSA. Tentou-se: %s" % rsa_key_path)
        if not os.path.isfile(certificate_path):
            raise Exception(u"Não foi possível encontrar Certificado. Tentou-se: %s" % certificate_path)
        cmd = GET_PEM_RAW_CMD % {'key_path':rsa_key_path, 'cert_path':certificate_path,}
        pem = os.popen(cmd).read()
        utils.remove_or_leave(rsa_key_path)
        utils.remove_or_leave(certificate_path)
        return pem

    # TODO: refatorar código e separar em várias funções
    def dump_filedaemon_config(self):
        """Gera arquivo de configuraçãodo cliente bacula-sd.conf."""
        import time
        
        fd_dict =   {'Name': self.computer_name, 
                    'FDport':'9102', #TODO: tratar porta do cliente
                    'Maximum Concurrent Jobs':'5',}
                    
        if self.computer_encryption:
            if self.computer_so == 'UNIX':
                fd_dict.update( {'PKI Signatures':'Yes',
                                'PKI Encryption':'Yes',
                                'PKI Keypair':'''"/etc/bacula/%s"''' % (self.computer_pem()),
                                'PKI Master Key':'''"/etc/bacula/master.cert"''',})
            elif self.computer_so == 'WIN':
                fd_dict.update( {'PKI Signatures':'Yes',
                                'PKI Encryption':'Yes',
                                'PKI Keypair':'''"C:\\\\Nimbus\\\\%s"''' % (self.computer_pem()),
                                'PKI Master Key':'''"C:\\\\Nimbus\\\\master.cert"''',})
            
        if self.computer_so == 'UNIX':
            fd_dict.update( {'WorkingDirectory':'/var/bacula/working ',
                            'Pid Directory':'/var/run ',})
        elif self.computer_so == 'WIN':
            fd_dict.update( {'WorkingDirectory':'''"C:\\\\Nimbus"''',
                            'Pid Directory':'''"C:\\\\Nimbus"''',})
        gconf = GlobalConfig.objects.get(pk=1)
        dir_dict =  {'Name':gconf.director_bacula_name(),
                    'Password':'''"%s"''' % (self.computer_password),}
        msg_dict =  {'Name':'Standard',
                    'director':'%s = all, !skipped, !restored' % (gconf.director_bacula_name()),}
        dump = []
    
        dump.append("#\n")
        # TODO: adicionar version stamp aqui
        dump.append("# Generated by Nimbus %s\n" % (time.strftime("%d-%m-%Y %H:%M:%S", time.localtime())))
        dump.append("#\n")
        dump.append("FileDaemon {\n")
        for k in fd_dict.keys():
            dump.append('''\t%(key)s = %(value)s\n''' % {'key':k,'value':fd_dict[k]})
        dump.append("}\n\n")
        dump.append("Director {\n")
        for k in dir_dict.keys():
            dump.append('''\t%(key)s = %(value)s\n''' % {'key':k,'value':dir_dict[k]})
        dump.append("}\n\n")
        dump.append("Messages {\n")
        for k in msg_dict.keys():
            dump.append('''\t%(key)s = %(value)s\n''' % {'key':k,'value':msg_dict[k]})
        dump.append("}\n\n")
        
        return ''.join(dump)

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
        from backup_corporativo.bkp.bacula import BaculaDatabase
        from backup_corporativo.bkp.sql_queries import CLIENT_RUNNING_JOBS_RAW_QUERY
        running_jobs_query = CLIENT_RUNNING_JOBS_RAW_QUERY % {'client_name':self.computer_bacula_name(),}
        running_jobs_cursor = BaculaDatabase.execute(running_jobs_query)
        return utils.dictfetch(running_jobs_cursor)

    def last_jobs(self):
        from backup_corporativo.bkp.bacula import BaculaDatabase
        from backup_corporativo.bkp.sql_queries import CLIENT_LAST_JOBS_RAW_QUERY
        last_jobs_query = CLIENT_LAST_JOBS_RAW_QUERY % {'client_name':self.computer_bacula_name(),}
        last_jobs_cursor = BaculaDatabase.execute(last_jobs_query)
        return utils.dictfetch(last_jobs_cursor)

    def run_test_job(self):
        """Sends an empty job running requisition to bacula for this computer"""
        from backup_corporativo.bkp.bacula import Bacula;
        Bacula.run_backup(JobName='Teste Conectividade', client_name=self.computer_bacula_name())

    def absolute_url(self):
        """Returns absolute url."""
        return "computer/%s" % (self.id)

    def view_url(self):
        """Returns absolute url."""
        return "computer/%s" % (self.id)

    def edit_url(self):
        """Returns absolute url."""
        return "computer/%s/edit" % (self.id)

    def delete_url(self):
        """Returns delete url."""
        return "computer/%s/delete" % (self.id)

    def config_dump_url(self):
        """Returns config dump url."""
        return "computer/%s/config_dump" % (self.id)

    def pem_dump_url(self):
        """Returns pem dump url."""
        return "computer/%s/pem_dump" % (self.id)

    def master_cert_dump_url(self):
        """Returns master cert dump url."""
        return "computer/master_certificate/"
   
    def run_test_url(self):
        """Returns run test url."""
        return "computer/%s/test" % (self.id)

    def key_cert_pem_url(self):
        return "computer/%s/key_cert_pem/" % (self.id)

    def __update_bacula_id(self):
        """Queries bacula database for client id"""
        from backup_corporativo.bkp.sql_queries import CLIENT_ID_RAW_QUERY
        from backup_corporativo.bkp.bacula import BaculaDatabase
        
        cliend_id_query = CLIENT_ID_RAW_QUERY % {'client_name':self.computer_bacula_name()}
        cursor = BaculaDatabase.cursor()
        cursor.execute(cliend_id_query)
        client_id = cursor.fetchone()
        self.computer_bacula_id = client_id and client_id[0] or self.NIMBUS_ERROR
        self.save()

    def __unicode__(self):
        return "%s (%s)" % (self.computer_name, self.computer_ip)

    # ClassMethods
    def master_rsa_key_path(cls):
        return utils.absolute_file_path("master.key","custom/crypt/")
    master_rsa_key_path = classmethod(master_rsa_key_path)
    
    def master_certificate_path(cls):
        return utils.absolute_file_path("master.cert","custom/crypt/")
    master_certificate_path = classmethod(master_certificate_path)
        
    # TODO: quando gerar certificado e master_key, enviar por email pro usuário
    def generate_master_rsa_key(cls):
        cls.generate_rsa_key(cls.master_rsa_key_path())
    generate_master_rsa_key = classmethod(generate_master_rsa_key)

    def generate_master_certificate(cls):
        cls.generate_certificate(cls.master_rsa_key_path(), cls.master_certificate_path())
    generate_master_certificate = classmethod(generate_master_certificate)

    def dump_master_certificate(cls):
        f = open(cls.master_certificate_path())
        dump = []
        for line in f:
            dump.append("%s") % line
            
        return '\n'.join(dump)
    dump_master_certificate = classmethod(dump_master_certificate)
