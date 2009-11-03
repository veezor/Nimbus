#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.utils.translation import ugettext_lazy
from django.forms import ModelForm
from django import forms

from backup_corporativo.bkp.models import *
from backup_corporativo.bkp import customfields as cfields

from keymanager import KeyManager

BOOLEAN_CHOICES = ((True,'Ativo'),(0,'Desativado'),)
BR_DATES = ['%d/%m/%Y']

class NewStrongBoxForm(forms.Form):
    sb_password = forms.CharField(
        label=u'Senha',
        max_length=255,
        widget=forms.PasswordInput(render_value=False)
    )
    sb_password_2 = forms.CharField(
        label=u'Confirme a Senha',
        max_length=255,
        widget=forms.PasswordInput(render_value=False)
    )
    
    #TODO: adicionar validação de tamanho e complexidade da senha.
    def clean_sb_password_2(self):
        """
        Confere que as duas senhas sao iguais.
        Caso nao sejam, dispara um erro de validaçao explicando isso.
        Aciona comando de criar drive.
        Caso drive não seja criado, dispara erro de validação explicando isso.
        """
        cleaned_data = self.cleaned_data
        password = cleaned_data.get("sb_password")
        password_2 = cleaned_data.get("sb_password_2")
        
        if password == password_2:
            km = KeyManager(password=password)
            drive_created = km.create_drive()
            if not drive_created:
                raise forms.ValidationError(
                    ugettext_lazy("Strongbox could not be created. Please contact support.")
                )
        else:
            raise forms.ValidationError(
                ugettext_lazy("Password confirmation doesn't match")
            )
        return password_2


class MountStrongBoxForm(forms.Form):
    """
    Aciona comando de montar o cofre.
    Caso cofre nao seja montado, dispara um erro de validaçao explicando isso.
    """
    sb_password = forms.CharField(
        label=u'Senha',
        max_length=255,
        widget=forms.PasswordInput(render_value=False)
    )
    
    def clean_sb_password(self):
        password = self.cleaned_data.get("sb_password")
        km = KeyManager(password=password)
        drive_mounted = km.mount_drive()
        if not drive_mounted:
            raise forms.ValidationError(
                ugettext_lazy("Unable to mount strongbox. Wrong password or corrupted strongbox.")
            )
        else:
            return password


class ChangePasswdStrongBoxForm(forms.Form):
    """
    Confere se os dois novos passwords digitados são iguais.
    Caso não sejam, dispara um erro de validação explicando isso.
    Aciona o comando de alterar a senha do cofre.
    Caso a senha do cofre não seja alterada, dispara um erro de validação
    explicando isso.
    """
    sb_new_password = forms.CharField(
        label=u'Nova Senha',
        max_length=255,
        widget=forms.PasswordInput(render_value=False)
    )
    sb_new_password_2 = forms.CharField(
        label=u'Confirme Nova Senha',
        max_length=255,
        widget=forms.PasswordInput(render_value=False)
    )
    sb_old_password = forms.CharField(
        label=u'Senha Atual',
        max_length=255,
        widget=forms.PasswordInput(render_value=False)
    )
    sb_backup_header = forms.BooleanField(
        label=u'Habilitar restauração?',
    )
    
    #TODO: adicionar validação de tamanho e complexidade da senha.
    def clean_sb_new_password_2(self):
        cleaned_data = self.cleaned_data
        new_password = cleaned_data.get("sb_new_password")
        new_password_2 = cleaned_data.get("sb_new_password_2")
        
        if new_password != new_password_2:
            raise forms.ValidationError(
                ugettext_lazy("New Password confirmation doesn't match")
            )
        return new_password_2
    
    def clean_sb_old_password(self):
        cleaned_data = self.cleaned_data
        old_password = cleaned_data.get("sb_old_password")
        new_password = cleaned_data.get("sb_new_password")
        new_password_2 = cleaned_data.get("sb_new_password_2")
        km = KeyManager()
        
        if new_password == new_password_2:
            pwd_changed = km.change_drive_password(old_password, new_password)
            if not password_changed:
                raise forms.ValidationError(
                    ugettext_lazy("Wrong password or strongbox header is corrupted.")
                )
        return old_password


class HeaderBkpForm(ModelForm):
	class Meta:
		model = HeaderBkp
		fields = ('headerbkp_name',)


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
			'director_port',
			'storage_port',
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

# WizardAuxForm serve para passar a informação de se o Wizard está ativo
# via POST para a view de criação dos objetos do wizard. Assim o menu
# "Onde, Oque, Quando" continua aparecendo.
class WizardAuxForm(forms.Form):
	wizard = forms.BooleanField(
		label="wizard_active",
		initial="False",
		widget=forms.HiddenInput)


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
		fields = ('path',)


class ScheduleAuxForm(forms.Form):
	schedule_type = forms.CharField(max_length=10,widget=forms.HiddenInput)
