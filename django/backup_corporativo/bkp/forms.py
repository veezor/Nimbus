#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.utils.translation import ugettext_lazy as _
from django.forms import ModelForm
from django.forms.util import ErrorList
from django import forms

import truecrypt
from keymanager import KeyManager

from backup_corporativo.bkp.models import *
from backup_corporativo.bkp import customfields as cfields

BOOLEAN_CHOICES = ((True,'Ativo'),(0,'Desativado'),)
BR_DATES = ['%d/%m/%Y']


class EncryptionForm(ModelForm):
    class Meta:
        model = Encryption
        fields = ('computer',)


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
        password = self.cleaned_data.get("sb_password")
        password_2 = self.cleaned_data.get("sb_password_2")
        
        print(self.cleaned_data)
        
        if password == password_2:
            km = KeyManager(password=password)
            drive_created = km.create_drive()
            if not drive_created:
                error = _("Strongbox could not be created. Please contact support.")
                raise forms.ValidationError(error)
        else:
            error = _("Password confirmation doesn't match.")
            raise forms.ValidationError(error)
        return self.cleaned_data


class UmountStrongBoxForm(forms.Form):
    sb_forceumount = forms.BooleanField(label="Forçar?", initial=False, required=False)
    

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
        try:
            drive_mounted = km.mount_drive()
        except truecrypt.PasswordError:
            error = _("Wrong password or corrupted strongbox.")
            raise forms.ValidationError(error)    
        if not drive_mounted:
            error = _("Unable to mount strongbox. Please contact support.")
            raise forms.ValidationError(error)
        return password


class ChangePwdStrongBoxForm(forms.Form):
    """
    Confere se os dois novos passwords digitados são iguais.
    Caso não sejam, dispara um erro de validação explicando isso.
    Aciona o comando de alterar a senha do cofre.
    Caso a senha do cofre não seja alterada, dispara um erro de validação
    explicando isso.
    """
    old_password = forms.CharField(
        label=u'Senha Atual',
        max_length=255,
        widget=forms.PasswordInput(render_value=False)
    )
    new_password = forms.CharField(
        label=u'Nova Senha',
        max_length=255,
        widget=forms.PasswordInput(render_value=False)
    )
    new_password_2 = forms.CharField(
        label=u'Confirme Nova Senha',
        max_length=255,
        widget=forms.PasswordInput(render_value=False)
    )
    
    #TODO: adicionar validação de tamanho e complexidade da senha.
    def clean(self):
        old_password = self.cleaned_data.get("old_password")
        new_password = self.cleaned_data.get("new_password")
        new_password_2 = self.cleaned_data.get("new_password_2")
        
        if new_password != new_password_2:
            error = _("New Password confirmation doesn't match.")
            if not 'new_password_2' in self._errors:
                self._errors['new_password_2'] = ErrorList()
            self._errors['new_password_2'].append(error)
            errors = True
        km = KeyManager()
        km.set_password(old_password)
        pwd_changed = km.change_drive_password(new_password)
        if not pwd_changed:
            error = _("Wrong password or strongbox header is corrupted.")
            if not 'old_password' in self._errors:
                self._errors['old_password'] = ErrorList()
            self._errors['old_password'].append(error)
            errors = True
        return self.cleaned_data


class HeaderBkpForm(ModelForm):
    drive_password = forms.CharField(
        label=u'Senha',
        max_length=255,
        widget=forms.PasswordInput(render_value=False)
    )
    class Meta:
        model = HeaderBkp
        fields = ('headerbkp_name',)
    
    def clean_drive_password(self):
        cleaned_data = self.cleaned_data
        headerbkp_name = cleaned_data.get("headerbkp_name")
        drive_password = cleaned_data.get("drive_password")
        km = KeyManager()
        km.set_password(drive_password)
        bkp_created = km.make_drive_backup(headerbkp_name)
        if not bkp_created:
            raise forms.ValidationError(
                ugettext_lazy("Wrong password.")
            )
        return drive_password


class EditHeaderBkpForm(ModelForm):
    class Meta:
        model = HeaderBkp
        fields = ('headerbkp_name',)


class RestoreHeaderBkpForm(ModelForm):
    drive_password = forms.CharField(
        label=u'Senha',
        max_length=255,
        widget=forms.PasswordInput(render_value=False)
    )
    class Meta:
        model = HeaderBkp
        fields = ('headerbkp_name',)

    def clean_drive_password(self):
        instance = getattr(self, 'instance', None)
        if instance and instance.id:
            headerbkp_name = instance.headerbkp_name
        else:
            raise forms.ValidationError(
                ugettext_lazy("Programming Error, please contact support.")
            )
        cleaned_data = self.cleaned_data
        drive_password = cleaned_data.get("drive_password")
        km = KeyManager()
        km.set_password(drive_password)
        bkp_restored = km.restore_drive_backup(headerbkp_name)
        if not bkp_restored:
            raise forms.ValidationError(
                ugettext_lazy("Wrong password.")
            )
        return drive_password

    def __init__(self, *args, **kwargs):
            super(RestoreHeaderBkpForm, self).__init__(*args, **kwargs)
            instance = getattr(self, 'instance', None)
            if instance and instance.id:
                self.fields['headerbkp_name'].widget.attrs['readonly'] = True


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
	FileSet = forms.BooleanField(widget=forms.HiddenInput, initial=True)
	Schedule = forms.BooleanField(widget=forms.HiddenInput, initial=True)
	schedule_type = forms.CharField(
		max_length=10,
		widget=forms.HiddenInput,
		initial="Monthly")
	Trigger = forms.BooleanField(widget=forms.HiddenInput, initial=True)


class RunProcedureForm(forms.Form):
	target_date = forms.DateField(label="Data", input_formats=BR_DATES)
	target_hour = forms.TimeField(label="Hora")


# WizardAuxForm serve para passar a informação de se o Wizard está ativo
# via POST para a view de criação dos objetos do wizard. Assim o menu
# "Onde, Oque, Quando" continua aparecendo.
class WizardAuxForm(forms.Form):
	wizard = forms.BooleanField(
		label="wizard_active",
		initial=False,
		widget=forms.HiddenInput)


class RunProcedureAuxForm(forms.Form):
	run_now = forms.BooleanField(label="Executar agora?")


class ComputerAuxForm(forms.Form):
	Procedure = forms.BooleanField(widget=forms.HiddenInput, initial=True)
	FileSet = forms.BooleanField(widget=forms.HiddenInput, initial=True)
	Schedule = forms.BooleanField(widget=forms.HiddenInput, initial=True)
	schedule_type = forms.CharField(
		max_length=10,
		widget=forms.HiddenInput,
		initial="Monthly")
	Trigger = forms.BooleanField(widget=forms.HiddenInput, initial=True)


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
