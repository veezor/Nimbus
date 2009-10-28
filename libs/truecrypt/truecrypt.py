#!/usr/bin/env python
# -*- coding: UTF-8 -*-


import os
import subprocess

TRUECRYPT_EXEC = "/usr/bin/truecrypt"


DRIVEPOINT = "/media/strongbox"
DRIVEFILE = "/root/strongbox.crypto"


COMMANDS = {
        "create" : """truecrypt -t -c --volume-type=Normal --size=1572864 --encryption=AES-Twofish-Serpent --hash=Whirlpool --filesystem=FAT --password=%s --keyfiles= --random-source=/dev/urandom %s""",
        "mount" : """sudo truecrypt -t --password=%s --keyfiles= --protect-hidden=no %s %s""",
        "umount" : """sudo truecrypt -t -d %s""",
        "umountf" : """sudo truecrypt -t -d -f %s""",
        "changepassword" : """truecrypt -t -C --password=%s --keyfiles= --new-keyfiles= --new-password=%s --random-source=/dev/urandom %s""",
        "backup": """truecrypt  -t --backup-headers --random-source=/dev/urandom  %s""",
        "restore" : """truecrypt -t --restore-headers  --random-source=/dev/urandom %s """ 
}




class TrueCryptNotFound(Exception):
    pass

class PermissionError(Exception):
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

    def call_command(self, cmd, *args ):
        cmd = self._generate_list( cmd, *args)
        p = self._get_popen(cmd)
        p.communicate()
        if self.debug:
            print " ".join(cmd)
            print p.stdout.read()
            print p.stderr.read()
        return not bool(p.returncode)

    def create_drive(self, password, drive=DRIVEFILE):
        return self.call_command( "create", password, drive)


    def mount_drive(self, password, drive=DRIVEFILE, target=DRIVEPOINT):
        #if os.getuid() != 0: SUDO
        #    raise PermissionError("root privileges required")

        return self.call_command( "mount", password, drive, target)

    def umount_drive(self, target=DRIVEPOINT):
        return self.call_command( "umount", target)

    def umountf_drive(self, target=DRIVEPOINT):
        return self.call_command( "umountf", target)

    def change_password(self, oldpassword, newpassword, drive=DRIVEFILE):
        return self.call_command( "changepassword", oldpassword, newpassword, drive)

    def make_backup(self, password, target, drive=DRIVEFILE):
        cmd = self._generate_list( "backup", drive)
        p = self._get_popen(cmd)
        stdout, stderr = p.communicate(self._MAKE_BACKUP_PARAMS % locals())
        if self.debug:
            print stdout
            print stderr
        return not bool( p.returncode )

    def restore_backup(self, password, backup, drive=DRIVEFILE):
        cmd = self._generate_list( "restore", drive)
        p = self._get_popen(cmd)
        stdout, stderr = p.communicate(self._RESTORE_BACKUP_PARAMS % locals())
        if self.debug:
            print stdout
            print stderr
        return not bool( p.returncode )

