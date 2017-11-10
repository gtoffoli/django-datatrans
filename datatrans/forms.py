'''
Created on 24/sep/2017

@author: giovanni
'''

import copy
from django.utils.translation import ugettext_lazy as _, string_concat
from django import forms

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
