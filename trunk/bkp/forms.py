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
from backup_corporativo.bkp.models import FileSet
from backup_corporativo.bkp.models import Storage
from backup_corporativo.bkp.models import ExternalDevice
from backup_corporativo.bkp.models import BandwidthRestriction
from backup_corporativo.bkp.models import DayOfTheWeek
# Custom
from backup_corporativo.bkp import customfields as cfields

#
#   Forms
#

class RestoreForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(RestoreForm, self).__init__(*args, **kwargs)
        self.fields['client_restore'].choices = [('', '----------')] + [(comp.computer_name, '%s (%s)' %(comp.computer_name, comp.ip)) for comp in Computer.objects.all()]

    client_restore = forms.ChoiceField(label="Computador", choices=(), widget=forms.Select())
    restore_path = cfields.FormPathField(label="Diretório", max_length=50)

class HiddenRestoreForm(forms.Form):
    fileset_name = forms.CharField(max_length=50, widget=forms.HiddenInput)
    client_source = forms.CharField(max_length=50, widget=forms.HiddenInput)
    target_dt = forms.CharField(max_length=50, widget=forms.HiddenInput)


class RestoreDumpForm(forms.Form):
	file = cfields.FormFileNimbusField(label=u'Arquivo para restaurar configurações')

class GlobalConfigForm(ModelForm):
    class Meta:
        model = GlobalConfig
        fields = ('bacula_name','storage_ip','storage_port','director_port','admin_mail','database_name','database_user','database_password')

class LoginForm(forms.Form):
    auth_login = forms.CharField(label=u'Usuário',max_length=20)
    auth_password = forms.CharField(label=u'Senha',max_length=50,widget=forms.PasswordInput(render_value=False))

class ComputerForm(ModelForm):
    class Meta:
        model = Computer
        fields = ('computer_name','ip','description')

class StorageForm(ModelForm):
    class Meta:
        model = Storage
        fields = ('storage_name', 'storage_ip', 'storage_port',
                  'storage_password', 'storage_description')
        
class ProcedureForm(ModelForm):
    class Meta:
        model = Procedure
        fields = ('procedure_name')

class ScheduleAuxForm(forms.Form):
    schedule_type = forms.CharField(max_length=10,widget=forms.HiddenInput, initial="Monthly")

class ProcedureAuxForm(forms.Form):
    FileSet = forms.BooleanField(widget=forms.HiddenInput, initial="True")
    Schedule = forms.BooleanField(widget=forms.HiddenInput, initial="True")
    schedule_type = forms.CharField(max_length=10,widget=forms.HiddenInput, initial="Monthly")
    Trigger = forms.BooleanField(widget=forms.HiddenInput, initial="True")


BR_DATES = ['%d/%m/%Y']   #sim, eh uma lista

class RunProcedureForm(forms.Form):
    target_date = forms.DateField(label="Data", input_formats=BR_DATES)
    target_hour = forms.TimeField(label="Hora")

class RunProcedureAuxForm(forms.Form):
    run_now = forms.BooleanField(label="Executar agora?")

class ComputerAuxForm(forms.Form):
    Procedure = forms.BooleanField(widget=forms.HiddenInput, initial="True")
    FileSet = forms.BooleanField(widget=forms.HiddenInput, initial="True")
    Schedule = forms.BooleanField(widget=forms.HiddenInput, initial="True")
    schedule_type = forms.CharField(max_length=10,widget=forms.HiddenInput, initial="Monthly")
    Trigger = forms.BooleanField(widget=forms.HiddenInput, initial="True")

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

class FileSetForm(ModelForm):
    class Meta:
        model = FileSet
        fields = ('path')

class ExternalDeviceForm(ModelForm):
    class Meta:
        model = ExternalDevice
        fields = ('device_name','uuid')

class ExternalDeviceEditForm(forms.Form):
    device_name = forms.CharField(label='Nome',max_length=20)



class BandwidthRestrictionForm(forms.Form):
    # TODO: import days of the week from its original place
	DAYS_OF_THE_WEEK = (
		('monday','Segunda'),
		('tuesday','Terça'),
		('wednesday','Quarta'),
		('thursday','Quinta'),
		('friday','Sexta'),
		('saturday','Sábado'),
		('sunday','Domingo')
	)

	#DAYS_LIST = DayOfTheWeek.objects.all()

	restrictiontime = forms.TimeField(label=u'Hora de Restrição',input_formats=['%H:%M'])
	restriction_value =  forms.IntegerField(label=u'Limite de Upload')
	days = forms.MultipleChoiceField(choices=DAYS_OF_THE_WEEK,widget=forms.CheckboxSelectMultiple())
