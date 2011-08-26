#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os

from django.conf import settings

from nimbus.schedules.models import Schedule
from nimbus.filesets.models import FileSet
from nimbus.computers.models import Computer
from nimbus.procedures.models import Procedure


class Trashmen(object):
    """Dont you know about a bird? Everybody that bird is a word!"""

    def orphan_objects(self):
        """Pega todos os objetos orfaos"""
        orphans = []
        # Schedules que não são modelos e não tem procedure
        schedules = Schedule.objects.filter(is_model=False,procedures__isnull=True)
        orphans += schedules
        
        # Filesets que não são modelos e não tem procedure
        filesets = FileSet.objects.filter(is_model=False,procedures__isnull=True)
        orphans += filesets

        return orphans
        
    def remove_orphan_objects(self):
        """Remove todos os objetos orfaos"""
        orphans = self.orphan_objects()
        for orphan in orphans:
            orphan.delete()

    def orphan_files(self):
        orphans = []
        orphans += self.orphan_computer_files()
        orphans += self.orphan_fileset_files()
        orphans += self.orphan_schedule_files()
        orphans += self.orphan_procedure_files()
        orphans += self.orphan_pool_files()
        return orphans

    def remove_orphan_files(self):
        orphans = self.orphan_files()
        for orphan in orphans:
            os.remove(orphan)
        
    def orphan_computer_files(self):
        orphans = []
        dir_path = settings.NIMBUS_COMPUTERS_DIR
        files = os.listdir(dir_path)
        computers = Computer.objects.all()
        computer_names = [computer.bacula_name for computer in computers]
        for f in files:
            if f not in computer_names:
                orphans.append("%s/%s" % (dir_path, f))
        return orphans
        
    def orphan_fileset_files(self):
        orphans = []
        dir_path = settings.NIMBUS_FILESETS_DIR
        files = os.listdir(dir_path)
        filesets = FileSet.objects.all()
        fileset_names = [fileset.bacula_name for fileset in filesets]
        for f in files:
            if f not in fileset_names:
                orphans.append("%s/%s" % (dir_path, f))
        return orphans

    def orphan_schedule_files(self):
        orphans = []
        dir_path = settings.NIMBUS_SCHEDULES_DIR
        files = os.listdir(dir_path)
        schedules = Schedule.objects.all()
        schedule_names = [schedule.bacula_name for schedule in schedules]
        for f in files:
            if f not in schedule_names:
                orphans.append("%s/%s" % (dir_path, f))
        return orphans

    def orphan_procedure_files(self):
        orphans = []
        dir_path = settings.NIMBUS_JOBS_DIR
        files = os.listdir(dir_path)
        procedures = Procedure.objects.all()
        procedure_names = [procedure.bacula_name for procedure in procedures]
        for f in files:
            if f not in procedure_names:
                orphans.append("%s/%s" % (dir_path, f))
        return orphans

    def orphan_pool_files(self):
        orphans = []
        dir_path = settings.NIMBUS_POOLS_DIR
        files = os.listdir(dir_path)
        procedures = Procedure.objects.all()
        pool_names = [procedure.pool_bacula_name() for procedure in procedures]
        for f in files:
            if f not in pool_names:
                orphans.append("%s/%s" % (dir_path, f))
        return orphans