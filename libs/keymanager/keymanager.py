#!/usr/bin/env python
# -*- coding: UTF-8 -*-



import os
from os.path import join
import subprocess

import encryptdevicemanager as EncDeviceManager


ENCRYPT_DEVICE = "/var/nimbus/strongbox.crypto"
MOUNTPOINT = "/media/strongbox"
OPENSSLCONFIG = "/etc/nimbus/ssl.conf"



def generate_pem(prefix, keyfile, certfile):
    f = file(keyfile)
    keycontent = f.read()
    f.close()

    f = file(certfile)
    certcontent = f.read()
    f.close()


    filepem = file( join( prefix, "client.pem"), "w")
    filepem.write( keycontent)
    filepem.write( certcontent)
    filepem.close()




def generate_and_save_keys(prefix):

    keyfilename = join(prefix,  "client.key")
    cmd = subprocess.Popen(["openssl", "genrsa", "-out", keyfilename, "2048"],
                           stdout=subprocess.PIPE)
    cmd.communicate()


    certfilename = join(prefix,  "client.cert")
    cmd = subprocess.Popen(["openssl", "req", "-new", 
                            "-key", keyfilename, "-x509",
                            "-config", OPENSSLCONFIG,
                            "-out",certfilename],
                            stdout=subprocess.PIPE)
    cmd.communicate()


    generate_pem( prefix, keyfilename, certfilename)
    return True


class KeyManager(object):

    def __init__(self, password=None, drive=ENCRYPT_DEVICE, 
                                      mountpoint=MOUNTPOINT):
        self.drive = drive
        self.password = password
        self.mountpoint = mountpoint
        self.devmanager = EncDeviceManager.Manager(self.drive, 
                                                   self.mountpoint)

    @property
    def mounted(self):
        return self.devmanager.is_mounted()

    def set_password(self, password):
        self.password = password

    def has_drive(self):
        return os.access(self.drive, os.R_OK)

    def create_drive(self):
        return self.devmanager.create(self.password)

    def get_client_path(self, client):
        return os.path.join( self.mountpoint, client )

    def get_client_path_file(self, client, path):
        return os.path.join( self.mountpoint, client, path)

    def generate_and_save_keys_for_client(self, client):
        self.mount_drive()
        dirpath = self.get_client_path(client)
        if not os.access(dirpath, os.W_OK):
            os.mkdir(dirpath)
        return generate_and_save_keys(dirpath)


    def mount_drive(self):

        if not os.access(self.mountpoint, os.W_OK):
            #os.mkdir(self.mountpoint)
            pass

        if not self.mounted:
            return self.devmanager.mount( self.password )
        return False


    def umount_drive(self, force=False):
        if force:
            return self.force_umount_drive()
        return self.devmanager.umount()

    
    def force_umount_drive(self):
        return self.devmanager.umountf()


    def change_drive_password(self, new_password):
        r = self.devmanager.change_password(self.password, 
                                           new_password)

        self.set_password( new_password )
        return r

    def make_drive_backup(self, backupfilename):
        return self.devmanager.make_backup( self.password, 
                                           backupfilename)

    def restore_drive_backup(self, backupfilename):
        return self.devmanager.restore_backup( self.password, 
                                               backupfilename)

    def remove_backup_file(self, backupfilename):
        return os.remove( backupfilename )
