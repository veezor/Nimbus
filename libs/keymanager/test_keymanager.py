#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os
import unittest
import tempfile
import M2Crypto
import keymanager




class KeyManagerTestWithoutBuild(unittest.TestCase):


    def setUp(self):
        self.key_manager = keymanager.KeyManager()


    def test_raises_build_exception(self):
        self.assertRaises( keymanager.BuildKeysNotCalled, lambda :self.key_manager.key_as_str)
        self.assertRaises( keymanager.BuildKeysNotCalled, lambda : self.key_manager.public_key_as_str)
        self.assertRaises( keymanager.BuildKeysNotCalled, lambda : self.key_manager.certificate_as_str)
        self.assertRaises( keymanager.BuildKeysNotCalled, lambda : self.key_manager.keys_as_str)
        self.assertRaises( keymanager.BuildKeysNotCalled, lambda : self.key_manager.pem)

        self.assertRaises( keymanager.BuildKeysNotCalled, self.key_manager.save_key, tempfile.mktemp())
        self.assertRaises( keymanager.BuildKeysNotCalled, self.key_manager.save_public_key, tempfile.mktemp())
        self.assertRaises( keymanager.BuildKeysNotCalled, self.key_manager.save_certificate, tempfile.mktemp())
        self.assertRaises( keymanager.BuildKeysNotCalled, self.key_manager.save_pem, tempfile.mktemp())

        self.assertRaises( keymanager.BuildKeysNotCalled, self.key_manager.save_keys_on_directory, tempfile.mkdtemp(), 'client')


    def test_constructor(self):
        self.assertEquals(self.key_manager.key, None)
        self.assertEquals(self.key_manager.public_key, None)
        self.assertEquals(self.key_manager.certificate, None)


    def test_build(self):
        config = dict(C='BR',
                      ST='Rio Grande Do Norte',
                      L='Natal',
                      O='Veezor',
                      OU='Veezor',
                      CN='Veezor')

        self.assertFalse(self.key_manager._build_keys)
        self.key_manager.build_keys(config)
        self.assertTrue(isinstance(self.key_manager.key, M2Crypto.RSA.RSA))
        self.assertTrue(isinstance(self.key_manager.public_key, M2Crypto.EVP.PKey))
        self.assertTrue(isinstance(self.key_manager.certificate, M2Crypto.X509.X509))
        self.assertTrue(self.key_manager._build_keys)



    def test_config_error(self):
        config = dict(C='BR',
                      ST='Rio Grande Do Norte',
                      L='Natal',
                      O='Veezor',
                      OU='Veezor',
                      CN='Veezor')


        def test(key):
            tmp_config = config.copy()
            del tmp_config[key]
            self.assertRaises( KeyError, self.key_manager.build_keys, tmp_config )


        for key in config:
            test(key)

#
#    def test_generate_key(self):
#        self.key_manager._generate_rsa_key()
#        self.assertTrue(isinstance(self.key_manager.key, M2Crypto.RSA.RSA))
#
#
#    def test_generate_public_key(self):
#        self.key_manager._generate_public_key()
#        self.assertTrue(isinstance(self.key_manager.public_key, M2Crypto.EVP.PKey))
#
#
#    def test_generate_certificate(self):
#        config = dict(C='BR',
#                      ST='Rio Grande Do Norte',
#                      L='Natal',
#                      O='Veezor',
#                      OU='Veezor',
#                      CN='Veezor')
#        self.key_manager._generate_certificate(config)
#        self.assertTrue(isinstance(self.key_manager.certificate, M2Crypto.X509.X509))



def read_file(filename):
    with file(filename) as f:
        return f.read()



class KeyManagerTest(unittest.TestCase):

    def setUp(self):
        self.key_manager = keymanager.KeyManager()
        self.config = dict(C='BR',
                      ST='Rio Grande Do Norte',
                      L='Natal',
                      O='Veezor',
                      OU='Veezor',
                      CN='Veezor')
        self.key_manager.build_keys(self.config)


    def _test_save(self, method, attr):
        filename = tempfile.mktemp()
        method(filename)
        self.assertTrue( os.path.exists(filename) )
        self.assertEqual( attr, read_file(filename) )


    def test_save_key(self):
        self._test_save( self.key_manager.save_key, self.key_manager.key_as_str )


    def test_save_public_key(self):
        self._test_save( self.key_manager.save_public_key, self.key_manager.public_key_as_str )


    def test_save_certificate(self):
        self._test_save( self.key_manager.save_certificate, self.key_manager.certificate_as_str )


    def test_save_pem(self):
        self._test_save( self.key_manager.save_pem, self.key_manager.pem )


    def test_pem(self):
        self.assertEqual(self.key_manager.pem, self.key_manager.key_as_str + self.key_manager.certificate_as_str)

    def test_save_keys(self):
        dirname = tempfile.mkdtemp()
        self.key_manager.save_keys_on_directory(dirname, 'client')
        self.assertTrue( os.path.exists(os.path.join(dirname, 'client.key')) )
        self.assertTrue( os.path.exists(os.path.join(dirname, 'client.cert') ))
        self.assertTrue( os.path.exists(os.path.join(dirname, 'client.pubkey') ))
        self.assertTrue( os.path.exists(os.path.join(dirname, 'client.pem') ))

    def test_save_keys_create_directory(self):
        dirname = tempfile.mktemp()
        self.key_manager.save_keys_on_directory(dirname, 'client')
        self.assertTrue( os.path.exists(dirname) )


    def test_keys_as_str(self):
        key, pub, cert, pem = self.key_manager.keys_as_str
        self.assertEqual(key, self.key_manager.key_as_str)
        self.assertEqual(pub, self.key_manager.public_key_as_str)
        self.assertEqual(cert, self.key_manager.certificate_as_str)
        self.assertEqual(pem, self.key_manager.pem)







if __name__ == "__main__":
    unittest.main()

