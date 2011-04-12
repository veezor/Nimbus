#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os
import hashlib
from functools import wraps
from M2Crypto import RSA, X509, EVP, m2


__all__ = ('KeyManager',)


class BuildKeysNotCalled(Exception):
    pass


def check_build(method):

    @wraps(method)
    def new_method(self, *args, **kwargs):
        if not self._build_keys:
            raise BuildKeysNotCalled('You must call build_keys method before this')
        return method(self, *args, **kwargs)

    return new_method



class KeyManager(object):

    def __init__(self):
        self.key = None
        self.public_key = None
        self.certificate = None
        self._build_keys = False



    def build_keys(self, certificate_config):
        """   requires certificate configuration. Configuration must be o mapping with keys ['C', 'CN', 'OU', 'O', 'L', 'ST']  """
        self._generate_rsa_key()
        self._generate_public_key()
        self._generate_certificate(certificate_config)
        self._build_keys = True


    def _generate_rsa_key(self):
        self.key = RSA.gen_key(2048, m2.RSA_F4)


    def _generate_public_key(self):
        self.public_key = EVP.PKey()
        self.public_key.assign_rsa(self.key)


    def _get_public_key_fingerprint(self):
        digest = hashlib.sha1(self.public_key.as_der()).hexdigest().upper()
        return ':'.join(digest[pos : pos+2] for pos in range(0, 40, 2))


    def _get_certificate_validity_in_days(self, days=3650):
        "return Days to seconds"
        return days * 24 * 60 * 60


    def _generate_certificate(self, config):

        self.certificate = X509.X509()
        self.certificate.set_serial_number(1)
        self.certificate.set_version(2)


        issuer = X509.X509_Name()
        issuer.CN = config['CN']
        issuer.OU = config['OU']
        issuer.O = config['O']
        issuer.L = config['L']
        issuer.ST = config['ST']
        issuer.C = config['C']


        self.certificate.set_issuer(issuer)
        self.certificate.set_pubkey(self.public_key)

        not_before = m2.x509_get_not_before(self.certificate.x509)
        not_after  = m2.x509_get_not_after(self.certificate.x509)
        m2.x509_gmtime_adj(not_before, 0)
        m2.x509_gmtime_adj(not_after, self._get_certificate_validity_in_days())


        self.certificate.add_ext(
            X509.new_extension('subjectKeyIdentifier', self._get_public_key_fingerprint() ))

        self.certificate.sign(self.public_key, 'sha1')



    @check_build
    def save_public_key(self, filename):
        self.public_key.save_key(filename, cipher=None)


    @check_build
    def save_key(self, filename):
        self.key.save_key(filename, cipher=None)


    @check_build
    def save_certificate(self, filename):
        self.certificate.save_pem(filename)


    @check_build
    def save_pem(self, filename):
        with file(filename, 'w') as f:
            f.write(self.pem)


    @check_build
    def save_keys_on_directory(self, directory, prefix):

        if not os.path.exists(directory):
            os.mkdir(directory)


        key_filename = os.path.join(directory, prefix + '.key')
        public_key_filename = os.path.join(directory, prefix + '.pubkey')
        certificate_filename = os.path.join(directory, prefix + '.cert')
        pem_filename = os.path.join(directory, prefix + '.pem')

        self.save_key(key_filename)
        self.save_public_key(public_key_filename)
        self.save_certificate(certificate_filename)
        self.save_pem(pem_filename)


    @property
    @check_build
    def key_as_str(self):
        return self.key.as_pem(cipher=None)

    @property
    @check_build
    def public_key_as_str(self):
        return self.public_key.as_pem(cipher=None)

    @property
    @check_build
    def certificate_as_str(self):
        return self.certificate.as_pem()

    @property
    @check_build
    def keys_as_str(self):
        return self.key_as_str, self.public_key_as_str, self.certificate_as_str, self.pem

    @property
    def pem(self):
        return self.key_as_str + self.certificate_as_str





