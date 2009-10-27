#!/usr/bin/env python
# -*- coding: UTF-8 -*-


import truecrypt
import os
from os.path import join
from M2Crypto import RSA, X509, EVP, m2




def generate_rsa_key():
    return RSA.gen_key(2048, m2.RSA_F4)


def make_public_key(rsa_key):
    pkey = EVP.PKey()
    pkey.assign_rsa(rsa_key, capture=False)
    return pkey


def make_certificate(public_key):
    cert = X509.X509()
    cert.set_version(cert.get_version())
    cert.set_pubkey(public_key)
    name = X509.X509_Name()
    name.CN =  'CN'
    name.OU = 'Nimbus'
    name.O = 'Linconet'
    name.L = 'Natal'
    name.ST = 'Rio Grande do Norte'
    name.C = 'BR'
    cert.set_subject_name(name)
    cert.sign(public_key, 'md5')
    return cert


def generate_keys():
    rsa = generate_rsa_key()
    pkey = make_public_key(rsa)
    cert = make_certificate(pkey)
    return rsa,cert


def generate_pem(rsa, cert):
    return rsa.as_pem(cipher=None) +  cert.as_pem()


def generate_keys_as_text():
    rsa, cert = generate_keys()
    pem = generate_pem(rsa, cert)
    return rsa.as_pem(cipher=None), cert.as_pem(), pem


def generate_and_save_keys(prefix):

    rsa,cert = generate_keys()

    rsa.save_key( join(prefix,  "client.key"), cipher=None)
    cert.save( join( prefix , "client.cert"))
    pem = generate_pem(rsa, cert)

    pem = file( join( prefix, "client.pem"), "w")
    pem.write( pem)
    pem.close()

    return rsa,cert


class KeyManager(object):

    def __init__(self, password, drive=truecrypt.DRIVEFILE):
        self.drive = drive
        self.password = password
        self.truecrypt = truecrypt.TrueCrypt()

    def has_drive(self):
        return os.access(truecrypt.DRIVEFILE, os.R_OK)

    def create_drive(self):
        return self.truecrypt.create_drive(self.password, self.drive)

    def generate_and_save_keys_for_client(self, client):
        self.mount_drive()
        dirpath = os.path.join( drive, client )
        if not os.access(dirpath):
            os.mkdir(dirpath)
        return generate_and_save_keys(dirpath)


    def mount_drive(self):
        return self.truecrypt.mount_drive( self.password, drive=self.drive)


    def umount_drive(self):
        return self.truecrypt.umount_drive( self.password, drive=self.drive)
