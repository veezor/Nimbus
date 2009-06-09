#!/usr/bin/python
# -*- coding: utf-8 -*-


# Misc
from django.forms import ModelForm
from django import forms
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

class LoginForm(forms.Form):
    auth_login = forms.CharField(label="Usuário",max_length=20)
    auth_password = forms.CharField(label="Senha",max_length=50)

class ComputerForm(ModelForm):
    class Meta:
        model = Computer
        fields = ('computer_name','ip','description')
        
class ProcedureForm(ModelForm):
    class Meta:
        model = Procedure
        fields = ('procedure_name','restore_path')

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
