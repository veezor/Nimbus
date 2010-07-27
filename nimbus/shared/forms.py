from django.forms import ModelForm


def form_without_uuid(modelcls):

    class Form(ModelForm):
        class Meta:
            exclude = ('uuid',)
            model = modelcls

    return Form


