#!/usr/bin/python
# -*- coding: utf-8 -*-

import re

from django.forms import ModelForm
from django.forms.util import ErrorList
from django import forms

from pytz import common_timezones, country_timezones, country_names

import truecrypt
from keymanager import KeyManager

from backup_corporativo.bkp.models import *
from backup_corporativo.bkp import customfields as cfields

BOOLEAN_CHOICES = ((True,'Ativo'),(0,'Desativado'),)
BR_DATES = ['%d/%m/%Y']
COUNTRY_CHOICES = country_names.items()
EMPTY_CHOICES = [('', '----------')]


class TimezoneForm(ModelForm):
    class Meta:
        model = TimezoneConfig
        fields = ('ntp_server', 'tz_country', 'tz_area')
    
    def load_area_choices(self, country_name):
        if country_name:
            self.fields['tz_area'].choices = \
                [('', '----------')] + \
                [(a,a) for a in sorted(country_timezones[country_name])]
        else:
            self.fields['tz_area'].choices = [('', '----------')]


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
        password = self.cleaned_data.get(u"sb_password")
        password_2 = self.cleaned_data.get(u"sb_password_2")

        if password == password_2:
            km = KeyManager(password=password)
            drive_created = km.create_drive()
            if not drive_created:
                error = u"Nao foi possível criar o cofre. Favor, contacte o suporte."
                raise forms.ValidationError(error)
        else:
            error = u"Confirmação da senha não confere."
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
        password = self.cleaned_data.get(u"sb_password")
        km = KeyManager(password=password)
        try:
            drive_mounted = km.mount_drive()
        except truecrypt.PasswordError:
            error = u"Senha incorreta ou o cofre está corrompido."
            raise forms.ValidationError(error)    
        if not drive_mounted:
            error = u"Não é possível abrir o cofre. Favor, contactar suporte."
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
        old_password = self.cleaned_data.get(u"old_password")
        new_password = self.cleaned_data.get(u"new_password")
        new_password_2 = self.cleaned_data.get(u"new_password_2")
        
        if new_password != new_password_2:
            error = u"Confirmação de senha não confere."
            if not 'new_password_2' in self._errors:
                self._errors['new_password_2'] = ErrorList()
            self._errors['new_password_2'].append(error)
            errors = True
        km = KeyManager()
        km.set_password(old_password)
        pwd_changed = km.change_drive_password(new_password)
        if not pwd_changed:
            error = u"Senha incorreta ou cofre está corrompido."
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
        headerbkp_name = cleaned_data.get(u"headerbkp_name")
        drive_password = cleaned_data.get(u"drive_password")
        km = KeyManager()
        km.set_password(drive_password.encode("utf-8"))
        uuid = NimbusUUID.generate_uuid_or_leave(self.instance)
        try:
            bkp_created = km.make_drive_backup(self.instance.filepath())
        except truecrypt.PasswordError:
            uuid.delete()
            error = u"Senha incorreta ou cofre está corrompido."
            raise forms.ValidationError(error)
        if not bkp_created:
            uuid.delete()
            error = u"Não foi possível criar ponto de restauração. Favor contactar suporte."
            raise forms.ValidationError(error)
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
            headerbkp_path = instance.filepath()
        else:
            error = u"Erro de programação. Favor contactar suporte"
            raise forms.ValidationError(error)
        cleaned_data = self.cleaned_data
        drive_password = cleaned_data.get(u"drive_password")
        km = KeyManager()
        km.set_password(drive_password)
        bkp_restored = km.restore_drive_backup(headerbkp_path)
        if not bkp_restored:
            error = u"Senha incorreta ou cofre está corrompido."
            raise forms.ValidationError(error)
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
		self.fields['client_restore'].choices = \
			[('', '----------')] + \
			[(comp.computer_bacula_name(), '%s (%s)' %  (comp.computer_name, comp.computer_ip)) \
			for comp in Computer.objects.all()]


class HiddenRestoreForm(forms.Form):
	fileset_name = forms.CharField(max_length=50, widget=forms.HiddenInput)
	client_source = forms.CharField(max_length=50, widget=forms.HiddenInput)
	target_dt = forms.CharField(max_length=50, widget=forms.HiddenInput)


class RestoreDumpForm(forms.Form):
	file = cfields.FormFileNimbusField(
		label=u'Arquivo para restaurar configurações')


class GlobalConfigForm(ModelForm):
    total_backup_size = forms.FloatField(label=u'Tamanho Total do Backup (GB)', max_value=1000, min_value=80)
    class Meta:
		model = GlobalConfig
		fields = (
			'globalconfig_name',
			'director_port',
			'storage_port',
            'total_backup_size',
			'offsite_on',
            'offsite_hour',
            'offsite_username',
            'offsite_password',
            'offsite_gateway_url',
            'offsite_upload_rate')



class OffsiteConfigForm(ModelForm):
	class Meta:
		model = GlobalConfig
		fields = ('offsite_on', 
                  'offsite_hour', 
                  'offsite_username',
                  'offsite_password',
                  'offsite_gateway_url',
                  'offsite_upload_rate')



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
#	offsite_on = forms.ChoiceField(
#		choices=BOOLEAN_CHOICES,
#		widget=forms.RadioSelect)


    pool_size = forms.CharField(label=u'Tamanho total ocupado')
    retention_time = forms.IntegerField(initial=30, min_value=1, max_value=365)

    class Meta:
		model = Procedure
		fields = ('procedure_name', 'storage', 'offsite_on', 'pool_size', 'retention_time')
        
    def max_pool_size(self):
        discount = self.instance.pool_size or 0
        return Procedure.max_pool_size(discount) 

    def clean_pool_size(self):
        re_pool_size = "^(?P<num>\d+(\.\d+)?)( )?(?P<unidade>M|m|GB|gb)$"
        result = re.search(re_pool_size, self.cleaned_data['pool_size'])
        
        if result:
            ipool_size = float(result.group("num"))
            mpool_size = self.max_pool_size()

            if result.group("unidade") == 'M' or result.group("unidade") == 'm':
                ipool_size = ipool_size/1000

            if ipool_size > mpool_size:
                error = u"Certifique-se que este valor seja menor ou igual a %s GB." % mpool_size
                raise forms.ValidationError(error)
            elif ipool_size < 0.5:
                error = u"Certifique-se que este valor seja maior ou igual a 0.5 GB."
                raise forms.ValidationError(error)
        else:
            error = u"Certifique-se que este valor esteja neste formato \"00 M\" ou \"00 GB\""
            raise forms.ValidationError(error)
        return ipool_size
            

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
        fields = ('interface_name','interface_address',
                'interface_network', 'interface_gateway',
                  'interface_netmask', 'interface_broadcast',
                  'interface_dns1', 'interface_dns2')


class PingForm(forms.Form):
	ping_address = forms.IPAddressField(label="Endereço IP")


class TraceRouteForm(forms.Form):
	traceroute_address = forms.IPAddressField(label="Endereço IP")


class NsLookupForm(forms.Form):
	nslookup_address = forms.CharField(label="Host")


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

class WizardNetworkForm(ModelForm):
    class Meta:
        model = Wizard
        fields = ('interface_name','interface_address',
                'interface_network', 'interface_gateway',
                  'interface_netmask', 'interface_broadcast',
                  'interface_dns1', 'interface_dns2')
        
class WizardGlobalConfigForm(ModelForm):
    total_backup_size = forms.IntegerField(label=u'Tamanho Total do Backup (GB)', max_value=1000, min_value=80)
    class Meta:
        model = Wizard
        fields = (
            'globalconfig_name',
            'director_port',
            'storage_port',
            'total_backup_size',
            'offsite_on')
        
class WizardTimezoneConfigForm(ModelForm):
    class Meta:
        model = Wizard
        fields = (
            'ntp_server',
            'tz_country',
            'tz_area')
        
    def load_area_choices(self, country_name):
        if country_name:
            self.fields['tz_area'].choices = \
                [('', '----------')] + \
                [(a,a) for a in country_timezones[country_name]]
        else:
            self.fields['tz_area'].choices = [('', '----------')]


class ExternalStorageForm(forms.Form):

    name = forms.CharField(label="Nome do computador")
    ip = forms.IPAddressField(label="Endereço IP")
    port = forms.IntegerField(label="Porta")
    device_name =  forms.CharField(label="Nome do dispositivo de armazenamento")
    password = forms.CharField(label="Senha", 
                               widget=forms.PasswordInput)
    description = forms.CharField(label="Descrição do computador",
                                  widget=forms.Textarea(attrs={'cols': 40, 
                                                               'rows': 5}))

    def load_data_from_device(self, device):
        storage = device.storage
        self.data = {
            'name' : storage.storage_name,
            'ip' :  storage.storage_ip,
            'port' : storage.storage_port,
            'description' : storage.storage_description,
            'password' : storage.storage_password,
            'device_name' : device.name
        }
        self.is_bound = True

