#!/usr/bin/python
# -*- coding: utf-8 -*-


# Misc
from django.forms import ModelForm
from django import forms
# Models
from backup_corporativo.bkp.models import GlobalConfig
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

class GlobalConfigForm(ModelForm):
    class Meta:
        model = GlobalConfig
        fields = ('bacula_name','storage_ip','storage_port','director_port','admin_mail')
        



class LoginForm(forms.Form):
    auth_login = forms.CharField(label=u'Usuário',max_length=20)
    auth_password = forms.CharField(label=u'Senha',max_length=50,widget=forms.PasswordInput(render_value=False))

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
