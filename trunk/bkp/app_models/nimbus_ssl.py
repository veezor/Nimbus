#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.core import serializers
from django.db import models
from django import forms
from backup_corporativo.bkp.models import TYPE_CHOICES, LEVEL_CHOICES, OS_CHOICES, DAYS_OF_THE_WEEK
from backup_corporativo.bkp import customfields as cfields
from backup_corporativo.bkp import utils
import os, string, time


class NimbusSSL(models.Model):
    nimbus_uuid = models.ForeignKey(NimbusUUID)
    
    def save(self):
        NimbusUUID.generate_uuid_or_leave(self)
        super(NimbusSSL, self).save()
    
    def uuid(self):
        return self.nimbus_uuid.uuid_hex

    def rsa_key_path(self):
        return utils.absolute_file_path(
            "%s.key" % self.uuid(),
            "custom/crypt/")

    def certificate_path(self):
        return utils.absolute_file_path(
            "%s.cert" % self.uuid(),
            "custom/crypt/")

    def pem_path(self):
        return utils.absolute_file_path(
            "%s.pem" % self.uuid(),
            "custom/crypt/")

    def __generate_rsa_key(self):
        if os.path.isfile(self.rsa_key_path()):
            pass # Não é necessário gerar novamente.
        else:
            from backup_corporativo.bkp.crypt_utils import GENERATE_RSA_KEY_RAW_CMD
            utils.create_or_leave(
                utils.absolute_dir_path('custom/crypt'))
            cmd = GENERATE_RSA_KEY_RAW_CMD % {
                'out':self.rsa_key_path()}
            os.popen(cmd).read()


    def __generate_certificate(self):
        if os.path.isfile(self.certificate_path()):
            pass # Não é necessário gerar novamente.
        else:
            from backup_corporativo.bkp.utils import CERTIFICATE_CONFIG_PATH
            from backup_corporativo.bkp.crypt_utils import GENERATE_CERT_RAW_CMD
            utils.create_or_leave(
                utils.absolute_dir_path('custom/crypt'))
            rsa_key_path = self.rsa_key_path()
            if not os.path.isfile(rsa_key_path):
                raise Exception(
                    u"Não foi possível encontrar Chave RSA. Tentou-se: %s" %  \
                    rsa_key_path)
            cmd = GENERATE_CERT_RAW_CMD % {
                'key_path':rsa_key_path,
                'conf':CERTIFICATE_CONFIG_PATH,
                'out':self.certificate_path()}
            os.popen(cmd).read()


    def dump_rsa_key(self):
        self.__generate_rsa_key()
        f = open(self.rsa_key_path())
        dump = []
        for line in f:
            dump.append(str(line))
            
        return '\n'.join(dump)    


    def dump_certificate(self):
        self.__generate_certificate()
        f = open(self.certificate_path())
        dump = []
        for line in f:
            dump.append(str(line)) 
        return '\n'.join(dump)    

    
    #TODO: verificar se o PEM que foi gerado é válido.
    def dump_pem(self):
        """
        Gera PEM do NimbusSSL
        PEM consiste na concatenação da chave
        e do certificado no mesmo arquivo.
        """
        from backup_corporativo.bkp.crypt_utils import GET_PEM_RAW_CMD
        rsa_key_path = self.rsa_key_path()
        certificate_path = self.certificate_path()
        if not os.path.isfile(rsa_key_path):
            raise Exception(
                u"Não foi possível encontrar Chave RSA. Tentou-se: %s" % \
                    rsa_key_path)
        if not os.path.isfile(certificate_path):
            raise Exception(
                u"Não foi possível encontrar Certificado. Tentou-se: %s" % \
                    certificate_path)
        cmd = GET_PEM_RAW_CMD % {
            'key_path':rsa_key_path,
            'cert_path':certificate_path,}
        pem = os.popen(cmd).read()
        utils.remove_or_leave(rsa_key_path)
        utils.remove_or_leave(certificate_path)
        return pem
    
    def build(self):
        ssl = NimbusSSL()
        ssl.save()
        return ssl
    build = classmethod(build)
