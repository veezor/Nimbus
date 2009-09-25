#!/usr/bin/python
# -*- coding: utf-8 -*-



from django.forms import ModelForm
from django import forms

from backup_corporativo.bkp.models import *
from backup_corporativo.bkp import customfields as cfields


BOOLEAN_CHOICES = ((True,'Ativo'),(0,'Desativado'),)
BR_DATES = ['%d/%m/%Y']

class RestoreCompForm(forms.Form):
	target_client = forms.ChoiceField(
		label="Computador",
		choices=(),
		widget=forms.Select())

	def __init__(self, *args, **kwargs):
		super(RestoreCompForm, self).__init__(*args, **kwargs)
		self.fields['target_client'].choices = \
			[('', '----------')] + \
			[(comp.id, '%s (%s)' %  (comp.computer_name, comp.computer_ip)) \
			for comp in Computer.objects.all()]


class RestoreProcForm(forms.Form):
	target_procedure = forms.ChoiceField(
		label="Procedimento",
		choices=(),
		widget=forms.Select())

	def load_choices(self, comp_id):
		self.fields['target_procedure'].choices = \
			[('', '----------')] + \
			[(proc.id, proc.procedure_name) \
			for proc in Procedure.objects.filter(computer=comp_id)]


class RestoreForm(forms.Form):
	client_restore = forms.ChoiceField(
		label="Computador",
		choices=(),
		widget=forms.Select())
	restore_path = cfields.FormPathField(label="Diretório", max_length=50)

	def __init__(self, *args, **kwargs):
		super(RestoreForm, self).__init__(*args, **kwargs)
		comp_name = comp.computer_name
		comp_ip = comp.computer_ip
		self.fields['client_restore'].choices = \
			[('', '----------')] + \
			[(comp_name, '%s (%s)' %  (comp_name, comp_ip)) \
			for comp in Computer.objects.all()]


class HiddenRestoreForm(forms.Form):
	fileset_name = forms.CharField(max_length=50, widget=forms.HiddenInput)
	client_source = forms.CharField(max_length=50, widget=forms.HiddenInput)
	target_dt = forms.CharField(max_length=50, widget=forms.HiddenInput)


class RestoreDumpForm(forms.Form):
	file = cfields.FormFileNimbusField(
		label=u'Arquivo para restaurar configurações')


class GlobalConfigForm(ModelForm):
	class Meta:
		model = GlobalConfig
		fields = (
			'globalconfig_name',
			'server_ip',
			'director_port',
			'storage_port',
			'database_name',
			'database_user',
			'database_password',
			'admin_mail',
			'offsite_on')


class OffsiteConfigForm(ModelForm):
	class Meta:
		model = GlobalConfig
		fields = ('offsite_on', 'offsite_hour')


class LoginForm(forms.Form):
	auth_login = forms.CharField(label=u'Usuário',max_length=20)
	auth_password = forms.CharField(
		label=u'Senha',
		max_length=50,
		widget=forms.PasswordInput(render_value=False))


class ComputerForm(ModelForm):
	class Meta:
		model = Computer
		fields = (
			'computer_name',
			'computer_ip',
			'computer_so',
			'computer_description',)


class StorageForm(ModelForm):
	class Meta:
		model = Storage
		fields = (
			'storage_name',
			'storage_ip',
			'storage_port',
			'storage_description')
		


class ProcedureForm(ModelForm):
	offsite_on = forms.ChoiceField(
		choices=BOOLEAN_CHOICES,
		widget=forms.RadioSelect)
	class Meta:
		model = Procedure
		fields = ('procedure_name', 'storage', 'offsite_on')


class ProcedureAuxForm(forms.Form):
	FileSet = forms.BooleanField(widget=forms.HiddenInput, initial="True")
	Schedule = forms.BooleanField(widget=forms.HiddenInput, initial="True")
	schedule_type = forms.CharField(
		max_length=10,
		widget=forms.HiddenInput,
		initial="Monthly")
	Trigger = forms.BooleanField(widget=forms.HiddenInput, initial="True")


class RunProcedureForm(forms.Form):
	target_date = forms.DateField(label="Data", input_formats=BR_DATES)
	target_hour = forms.TimeField(label="Hora")


class RunProcedureAuxForm(forms.Form):
	run_now = forms.BooleanField(label="Executar agora?")


class ComputerAuxForm(forms.Form):
	Procedure = forms.BooleanField(widget=forms.HiddenInput, initial="True")
	FileSet = forms.BooleanField(widget=forms.HiddenInput, initial="True")
	Schedule = forms.BooleanField(widget=forms.HiddenInput, initial="True")
	schedule_type = forms.CharField(
		max_length=10,
		widget=forms.HiddenInput,
		initial="Monthly")
	Trigger = forms.BooleanField(widget=forms.HiddenInput, initial="True")


class ScheduleForm(ModelForm):
	class Meta:
		model = Schedule
		fields = ('type')


class WeeklyTriggerForm(ModelForm):
	class Meta:
		model = WeeklyTrigger
		fields = (
			'sunday',
			'monday',
			'tuesday',
			'wednesday',
			'thursday',
			'friday',
			'saturday',
			'hour',
			'level')


class NetworkInterfaceEditForm(ModelForm):
	class Meta:
		model = NetworkInterface
		fields = ('interface_address','interface_gateway',)


class MonthlyTriggerForm(ModelForm):
	class Meta:
		model = MonthlyTrigger
		fields = ('hour','level','target_days')


class FileSetForm(ModelForm):
	class Meta:
		model = FileSet
		fields = ('path')


class ScheduleAuxForm(forms.Form):
	schedule_type = forms.CharField(max_length=10,widget=forms.HiddenInput)
