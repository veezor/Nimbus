#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.core import management

from backup_corporativo.bkp.models import Computer
from backup_corporativo.bkp.app_models.computer import ComputerLimitExceeded
from backup_corporativo.bkp.tests import NimbusUnitTest

class ComputerUnitTest(NimbusUnitTest):
    def setUp(self):
        for i in range(1, 14):            
            Computer.objects.get_or_create(computer_name='pc_teste_%s' % i,
                                           computer_ip='10.10.10.10',
                                           computer_so='UNIX')
        

    # Criação do computador deve gerar password e uuid
    def test_0(self):
        computer = Computer.objects.get(pk=1)
        current_passwd = computer.computer_password
        emsg = "Password deve ser gerado ao criar computador"
        self.assertNotEqual(current_passwd, computer.NIMBUS_BLANK, msg=emsg)
        emsg = "UUID deve ser gerado ao criar computador"
        self.assertTrue(computer.nimbus_uuid, msg=emsg)

    # Atualização do computador não deve mudar password e uuid
    def test_1(self):
        computer = Computer.objects.get(pk=1)
        old_password = computer.computer_password
        old_uuid = computer.nimbus_uuid
        
        computer.computer_name = 'pc_teste_novo'
        computer.save()
        
        emsg = "Password não deve mudar ao alterar computador"
        self.assertEquals(old_password, computer.computer_password, msg=emsg)
        emsg = "UUID não deve mudar ao alterar computador"
        self.assertEquals(old_uuid, computer.nimbus_uuid, msg=emsg)

    # Deve ser possível cadastrar apenas 14 computadores
    def test_2(self):
        computer = Computer(computer_name='Deve Falhar',
                            computer_so='WIN', 
                            computer_ip='1.1.1.1')

        self.assertRaises(ComputerLimitExceeded,computer.save)