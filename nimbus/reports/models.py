#!/usr/bin/env python
# -*- coding: UTF-8 -*-


import re
import socket
import fileinput

from django.db import models
from django.conf import settings
from django.core.mail import send_mail as django_send_email


from nimbus.shared.fields import check_domain
from nimbus.libs.template import render_to_string
from nimbus.bacula.models import Job
from nimbus.base.models import SingletonBaseModel as BaseModel

EMAIL_TEST_SUBJECT=u"Nimbus: Email de teste"
EMAIL_TEST_MESSAGE=u"""
Este email foi enviado a seu pedido para verificação da configuração de email do Nimbus.
"""
DEFAULT_SOCKET_TIMEOUT=10
socket.setdefaulttimeout(DEFAULT_SOCKET_TIMEOUT)


FIELD_RE = ":\s*(.*)"

REPORT_EXTRA_FIELDS = [
    "Rate",
    "Software Compression",
    "Encryption"
]


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

    class Meta:
        verbose_name = u"Configuração de email"



def send_email(subject, message):
    conf = EmailConf.get_instance()
    settings.EMAIL_HOST = conf.email_host
    settings.EMAIL_PORT = conf.email_port
    if conf.email_user and conf.email_password:
        settings.EMAIL_HOST_USER = conf.email_user
        settings.EMAIL_HOST_PASSWORD = conf.email_password
        settings.EMAIL_USE_TLS = conf.tls_support

    if conf.active:
        django_send_email(subject, message, conf.email_user, [conf.send_to])


def send_hello_message():
    send_email(EMAIL_TEST_SUBJECT, EMAIL_TEST_MESSAGE)


def get_field_from_txt(field_name, txt):
    expr = re.compile( field_name + FIELD_RE )
    return expr.findall(txt)[0]



def get_report_extra_fields(txt):
    result = {}
    for field in REPORT_EXTRA_FIELDS:
        try:
            field_value = get_field_from_txt(field, txt)
        except IndexError:
            field_value = u'Não disponível'

        result[field] = field_value


    return result


def get_stdin():
    lines = []
    for line in fileinput.input(files="-"):
        lines.append(line)

    return "".join(lines)



def send_email_report(job_id):


    conf = EmailConf.get_instance()
    if not conf.active:
        return

    job = Job.objects.get(jobid=job_id)
    procedure = job.procedure
    computer = procedure.computer

    stdin = get_stdin()
    extra_fields = get_report_extra_fields(stdin)

    fields = {
        "computer" : computer,
        "procedure" : procedure,
        "job" : job,
        "rate" : extra_fields["Rate"],
        "compression" : extra_fields["Software Compression"],
        "encryption" : extra_fields["Encryption"],
        "stdin" : stdin
    }
    message = render_to_string("email_report", **fields)
    subject = render_to_string("subject", **fields).strip()
    send_email(subject, message)
