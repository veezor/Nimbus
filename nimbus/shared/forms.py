from django.forms import ModelForm


def form(modelcls):

    class Form(ModelForm):
        class Meta:
            model = modelcls

    return Form


