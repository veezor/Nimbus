# -*- coding: UTF-8 -*-

from nimbus.computers import models
from django import forms
from django.forms import widgets
from django.forms.models import inlineformset_factory, BaseInlineFormSet
from nimbus.shared import forms as nimbus_forms
from django.forms import models as django_models

class TriggerBaseForm(BaseInlineFormSet):

    def add_fields(self, form, index):
        super(TriggerBaseForm, self).add_fields(form, index)
        form.fields['active'] = forms.BooleanField()

def make_form(modeltype, exclude_fields=None):

    class Form(forms.ModelForm):
        formfield_callback = nimbus_forms.make_custom_fields
        class Meta:
            model = modeltype
            exclude = exclude_fields

    return Form

class ComputerForm(django_models.ModelForm):
    name = forms.CharField(label=u'Nome do Computador', widget=widgets.TextInput(attrs={'class': 'text'}))
    address = forms.CharField(label=u'Endereço de Rede', widget=widgets.TextInput(attrs={'class': 'text'}))
    
    class Meta:
        model = models.Computer

class ComputerGroupForm(django_models.ModelForm):
    class Meta:
        model = models.ComputerGroup

#ComputerForm = make_form(models.Computer)