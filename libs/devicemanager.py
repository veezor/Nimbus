#!/usr/bin/env python
# -*- coding: UTF-8 -*-


import os
from subprocess import check_call, CalledProcessError



PMOUNT="/usr/bin/pmount"
PUMOUNT="/usr/bin/pumount"
DISK_LABELS_PATH="/dev/disk/by-label"
MOUNT_PATH_DIR="/media"


class MountError(Exception):
    pass

class UmountError(Exception):
    pass



def list_disk_labels():
    try:
        return os.listdir(DISK_LABELS_PATH)
    except OSError, e:
        return []


def list_devices():
    return [ StorageDeviceManager(label) for label in list_disk_labels() ]


class StorageDeviceManager(object):

    def __init__(self, labelname):
        self.labelname = labelname


    def __repr__(self):
        return 'StorageDeviceManager(%s)' % self.labelname

    def _storage_info(self):
        if self.mounted:
            info = os.statvfs(self.mountpoint)
            total = info.f_bsize * info.f_blocks
            free = info.f_bsize * info.f_bfree
            used = total - free
            return total, used, free
        else:
            return 0,0,0


    @property
    def mounted(self):
        f = file("/etc/mtab")
        content = f.read()
        f.close()
        return self.device in content

    @property
    def device(self):
        device_label_file = os.path.join(DISK_LABELS_PATH, self.labelname)
        link = os.readlink(device_label_file)
        return os.path.abspath(os.path.join(DISK_LABELS_PATH, link))

    @property
    def mountpoint(self):
        return os.path.join(MOUNT_PATH_DIR, self.labelname)


    @property
    def available_size(self):
        total, used, free = self._storage_info()
        return free


    @property
    def used_size(self):
        total, used, free = self._storage_info()
        return used


    @property
    def size(self):
        total, used, free = self._storage_info()
        return total


    def mount(self):
        if not self.mounted:
            try:
                r = check_call([PMOUNT, self.device, self.labelname])
            except CalledProcessError, e:
                raise MountError(e)
            if r:
                raise MountError("mount return is %d" % r)


    def umount(self):
        if self.mounted:
            try:
                r = check_call([PUMOUNT, self.device])
            except CalledProcessError, e:
                raise UmountError(e)
            if r:
                raise UmountError("umount return is %d" % r)


