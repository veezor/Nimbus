#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#Copyright © 2010, 2011 Veezor Network Intelligence (Linconet Soluções em Informática Ltda.), <www.veezor.com>
#
# This file is part of Nimbus Opensource Backup.
#
#    Nimbus Opensource Backup is free software: you can redistribute it and/or 
#    modify it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License.
#
#    Nimbus Opensource Backup is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Nimbus Opensource Backup.  If not, see <http://www.gnu.org/licenses/>.
#
#In this file, along with the Nimbus Opensource Backup code, it may contain 
#third part code and software. Please check the third part software list released 
#with every Nimbus Opensource Backup copy.
#
#You can find the correct copyright notices and license informations at 
#their own website. If your software is being used and it's not listed 
#here, or even if you have any doubt about licensing, please send 
#us an e-mail to law@veezor.com, claiming to include your software.
#


import tempfile
from keymanager import keymanager
from django.conf import settings
from nimbus.computers.models import Computer



########### 1.0 to 1.1


class ComputerUpdateError(Exception):
    pass


def _update_certificate_and_pem(computer):

    key_filename = tempfile.mktemp()
    certificate_filename = tempfile.mktemp()

    crypto_info = computer.crypto_info

    crypto_info.save_key(key_filename)
    crypto_info.certificate = keymanager.generate_certificate(key_filename,
                                                              certificate_filename,
                                                              settings.NIMBUS_SSLCONFIG)
    crypto_info.pem = keymanager.generate_pem( crypto_info.key, crypto_info.certificate )
    crypto_info.save()

    computer.configure()


def _computer_is_online(computer):
    try:
        msg = "\tVerificando client %s...." % computer
        print msg,
        computer.get_file_tree('/')
        print "[Online]"
        return True
    except Exception:
        print "[Offline]"
        return False


def _check_computers(computers):
    computers_online = [ c for c in computers if _computer_is_online(c)]
    if len(computers) != len(computers_online):
        raise ComputerUpdateError("A client is offline")


def _update_computers_crypto_info(computers):
    for computer in computers:
        msg = "\t%s" % computer
        print msg + "....",
        _update_certificate_and_pem(computer)
        print "[Atualizado]"


def update_10_to_11():
    computers = Computer.objects.all()
    print "%d clientes para atualizar:" % len(computers)
    print "Verificando conexão com clientes...."
    _check_computers(computers)
    print "Conexão com clientes estabelecida...Ok"
    print "Atualizando configuração dos clientes....."
    _update_computers_crypto_info(computers)
    print "Update realizado com sucesso!"



####### end 1.0 to 1.1
