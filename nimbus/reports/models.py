#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from django.db import models
from django.conf import settings
from django.core.mail import send_mail as django_send_email



from nimbus.shared.fields import check_domain
from nimbus.base.models import SingletonBaseModel as BaseModel

EMAIL_TEST_SUBJECT=u"Nimbus: Email de teste"
EMAIL_TEST_MESSAGE=u"""
Este email foi enviado a seu pedido para verificação da configuração de email do Nimbus.
"""


class EmailConf(BaseModel):
    active = models.BooleanField(u"Ativo",default=False)
    send_to = models.EmailField(u"Enviar para",max_length=255)
    email_host = models.CharField(u"Host", max_length=255,
                                  validators=[check_domain])
    email_port = models.IntegerField(u"Porta")
    email_user = models.CharField(u"Nome do usuário",max_length=255, 
                                  blank=True, null=True)
    email_password = models.CharField(u"Senha",max_length=255,
                                      blank=True, null=True)
    tls_support =  models.BooleanField(u"TLS",default=False)




def send_email(subject, message):
    conf = EmailConf.get_instance()
    settings.EMAIL_HOST = conf.email_host
    settings.EMAIL_PORT = conf.email_port
    if conf.email_user and conf.email_password:
        settings.EMAIL_HOST_USER = conf.email_user
        settings.EMAIL_HOST_PASSWORD = conf.email_password
        settings.EMAIL_USE_TLS = conf.tls_support
    from_email = '%s@%s' % (conf.email_user, conf.email_host)
    django_send_email(subject, message, from_email, [conf.send_to])




def send_hello_message():
    send_email(EMAIL_TEST_SUBJECT, EMAIL_TEST_MESSAGE)
