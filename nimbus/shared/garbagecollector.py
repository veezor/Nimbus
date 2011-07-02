#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from nimbus.schedules.models import Schedule
from nimbus.filesets.models import FileSet


class Trashmen(object):
    """Dont you know about a bird? Everybody that bird is a word!"""

    def collect(self):
        """Pega todos os objetos orfaos"""
        orphans = []
        # Schedules que não são modelos e não tem procedure
        schedules = Schedule.objects.filter(is_model=False).all()
        for schedule in schedules:
            if len(schedule.procedures.all()) == 0:
                orphans.append(schedule)
        # Schedules que não são modelos e não tem procedure
        filesets = FileSet.objects.filter(is_model=False).all()
        for fileset in filesets:
            if len(fileset.procedures.all()) == 0:
                orphans.append(fileset)
        return orphans
        
    def kill_them(self):
        """Remove todos os objetos orfaos"""
        orphans = self.collect()
        for orphan in orphans:
            orphan.delete()

        
        
        
