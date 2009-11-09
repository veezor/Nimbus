#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.db import models
from django import forms
from backup_corporativo.bkp import utils
from backup_corporativo.bkp.app_models.nimbus_uuid import NimbusUUID


class HeaderBkp(models.Model):
    headerbkp_name = models.CharField("Nome", max_length=50, unique=True)
    nimbus_uuid = models.ForeignKey(NimbusUUID)
    
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
        NimbusUUID.generate_uuid_or_leave(self)
        super(HeaderBkp, self).save()

    def filename(self):
        return "%s_headerbkp" % self.nimbus_uuid.uuid_hex

    def created_on(self):
        return self.nimbus_uuid.uuid_created_on

    def edit_url(self):
        return "strongbox/headerbkp/%s/edit" % self.id
    
    def delete_url(self):
        return "strongbox/headerbkp/%s/delete" % self.id

    def restore_url(self):
        return "strongbox/headerbkp/%s/restore" % self.id
