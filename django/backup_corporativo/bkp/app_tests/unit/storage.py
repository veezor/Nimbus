#!/usr/bin/env python
# -*- coding: utf-8 -*-

from backup_corporativo.bkp.models import Storage
from backup_corporativo.bkp.tests import NimbusUnitTest

class StorageUnitTest(NimbusUnitTest):
    
    def setUp(self):
        Storage.objects.get_or_create(storage_name='storage_test',
                                     storage_description='descrição de teste')
        self.storage = Storage.objects.get(pk=1)

    # Criação do storage deve gerar password e uuid 
    def test_0(self):
        password = self.storage.storage_password
        uuid = self.storage.nimbus_uuid
        
        emsg = 'Password deve ser gerado ao criar storage'
        self.assertNotEqual(password, self.storage.NIMBUS_BLANK, msg=emsg)
        emsg = 'UUID deve ser gerado ao criar storage'
        self.assertNotEqual(uuid, self.storage.NIMBUS_BLANK, msg=emsg)
    
    # Atualização do storage não deve alterar password e uuid
    def test_1(self):
        old_password = self.storage.storage_password
        old_uuid = self.storage.nimbus_uuid
        
        self.storage.storage_name = 'alteração no storage'
        self.storage.save()
        
        new_password = self.storage.storage_password
        new_uuid = self.storage.nimbus_uuid
        
        emsg = 'Password não deve mudar ao alterar storage'
        self.assertEquals(old_password, new_password, msg=emsg)
        emsg = 'UUID não deve mudar ao alterar storage'
        self.assertEquals(old_uuid, new_uuid, msg=emsg)