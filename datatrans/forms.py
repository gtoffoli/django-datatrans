import copy

from django.conf import settings
from django import forms
from django.utils.translation import ugettext_lazy as _
"""
if settings.DJANGO_VERSION == 1:
    from django.utils.translation import string_concat
if settings.DJANGO_VERSION == 2:
"""
from django.utils.text import format_lazy
def string_concat(*strings):
    return format_lazy('{}' * len(strings), *strings)

class ModelTranslationForm(forms.Form):
    def __init__(self, *args, **kwargs):
        form_field = kwargs.pop('form_field')
        form_field_label = form_field.label
        translation_field_name = kwargs.pop('translation_field_name')
        super(ModelTranslationForm, self).__init__(*args, **kwargs)
        language_code = translation_field_name.split('_')[-1].upper()
        label = '%s - %s' % (form_field_label, language_code)
        self.fields[translation_field_name] = copy.copy(form_field)
        self.fields[translation_field_name].label = label
