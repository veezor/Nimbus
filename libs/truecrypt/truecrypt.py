#!/usr/bin/env python
# -*- coding: UTF-8 -*-


import os
import subprocess
import logging


TRUECRYPT_EXEC = "/usr/bin/truecrypt"


DRIVEPOINT = "/media/strongbox"
DRIVEFILE = "/tmp/strongbox.crypto"


COMMANDS = {
        "create" : """truecrypt -t -c --volume-type=Normal --size=1572864 --encryption=AES-Twofish-Serpent --hash=Whirlpool --filesystem=FAT --password=%s --keyfiles= --random-source=/dev/urandom %s""",
        "mount" : """sudo truecrypt -t --password=%s --keyfiles= --protect-hidden=no %s %s""",
        "umount" : """sudo truecrypt -t -d %s""",
        "umountf" : """sudo truecrypt -t -d -f %s""",
        "changepassword" : """truecrypt -t -C --password=%s --keyfiles= --new-keyfiles= --new-password=%s --random-source=/dev/urandom %s""",
        "backup": """truecrypt  -t --backup-headers --random-source=/dev/urandom  %s""",
        "restore" : """truecrypt -t --restore-headers  --random-source=/dev/urandom %s """,
        "is_mounted" : """truecrypt -t -l""" 
}




class TrueCryptNotFound(Exception):
    pass

class PermissionError(Exception):
    pass

class PasswordError(Exception):
    pass


def has_truecrypt():
    return os.access( TRUECRYPT_EXEC, os.X_OK )



class TrueCrypt(object):

    _MAKE_BACKUP_PARAMS = "%(password)s\n\nn\ny\n%(target)s\n"      # 1 - password
                                                                    # 2 - keyfiles
                                                                    # 3 - contain hidden volumes
                                                                    # 4 - want to create volume header backup
                                                                    # 5 - dest filename

    _RESTORE_BACKUP_PARAMS = "2\ny\n%(backup)s\n%(password)s\n\n"   # 1 - external backup
                                                                    # 2 - you want to restore volume header
                                                                    # 3 - backup filename 
                                                                    # 4 - password of backup
                                                                    # 5 - keyfiles

    def __init__(self, debug=False):
        self.debug = debug
        if not has_truecrypt():
            raise TrueCryptNotFound("TrueCrypt executable not found")

    def _get_popen(self, cmd):
        return subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                stderr = subprocess.PIPE )

    def _generate_list(self, cmd, *args):
        cmd = COMMANDS[cmd].split()
        index = 0
        for i,param in enumerate(cmd):
            if "%s" in param:
                cmd[i] = cmd[i] % args[index]
                index += 1
        return cmd

    def call_command(self, cmd, params=None, input=None):
        cmd = self._generate_list( cmd, *params)
        p = self._get_popen(cmd)
        stdout, stderr = p.communicate(input)
        if self.debug:
            logger = logging.getLogger(__name__)
            msg = "Executando o comando: %s\nStdout: %s\nStderr: %s\nReturn code: %s"
            logger.info( msg % (" ".join(cmd),stdout,stderr,p.returncode ))
        return (not bool(p.returncode)),stdout,stderr

    def create_drive(self, password, drive=DRIVEFILE):
        return self.call_command( "create", params=(password, drive))[0]


    def mount_drive(self, password, drive=DRIVEFILE, target=DRIVEPOINT):
        #if os.getuid() != 0: SUDO
        #    raise PermissionError("root privileges required")

        ok, stdout, stderr = self.call_command( "mount", params=(password, drive, target))
        if stdout.startswith("Incorrect password"):
            raise PasswordError("Incorrect password")
        return ok

    def umount_drive(self, target=DRIVEPOINT):
        return self.call_command( "umount", params=(target,))[0]

    def umountf_drive(self, target=DRIVEPOINT):
        return self.call_command( "umountf", params=(target,))[0]

    def change_password(self, oldpassword, newpassword, drive=DRIVEFILE):
        return self.call_command( "changepassword", 
                                  params=(oldpassword, newpassword, drive))[0]

    def make_backup(self, password, target, drive=DRIVEFILE):
        ok, stdout, stderr = self.call_command( "backup", params=(drive,),
                                 input = self._MAKE_BACKUP_PARAMS % locals())

        if "Incorrect password" in stdout:
            raise PasswordError("Incorrect password")
        return ok

    def restore_backup(self, password, backup, drive=DRIVEFILE):
        ok, stdout, stderr = self.call_command( "restore", params=(drive,),
                                 input = self._RESTORE_BACKUP_PARAMS % locals())
        if "Incorrect password" in stderr:
            raise PasswordError("Incorrect password")
        return ok

    def is_mounted(self, drive=DRIVEFILE):
        ok, stdout, stderr = self.call_command( "is_mounted", params=(drive,)) 
        if ok == True and drive in stdout:
            return True
        return False


