#!/usr/bin/python
# -*- coding: utf-8 -*-


# Misc
from django.forms import ModelForm
# Models
from backup_corporativo.bkp.models import Computer
from backup_corporativo.bkp.models import Procedure
from backup_corporativo.bkp.models import Schedule
from backup_corporativo.bkp.models import WeeklyTrigger
from backup_corporativo.bkp.models import MonthlyTrigger
from backup_corporativo.bkp.models import UniqueTrigger
from backup_corporativo.bkp.models import FileSet

#
#   Forms
#

class ComputerForm(ModelForm):
    class Meta:
        model = Computer


class ProcedureForm(ModelForm):
    class Meta:
        model = Procedure
        fields = ('name','restore_path')

class ScheduleForm(ModelForm):
    class Meta:
        model = Schedule
        fields = ('type')

class WeeklyTriggerForm(ModelForm):
    class Meta:
        model = WeeklyTrigger
        fields = ('sunday','monday','tuesday','wednesday','thursday','friday','saturday','hour','level')

class MonthlyTriggerForm(ModelForm):
    class Meta:
        model = MonthlyTrigger
        fields = ('hour','level','target_days')

class UniqueTriggerForm(ModelForm):
    class Meta:
        model = UniqueTrigger
        fields = ('target_date','hour','level')

class FileSetForm(ModelForm):
    class Meta:
        model = FileSet
        fields = ('path')