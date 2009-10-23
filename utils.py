from django.conf import settings
from datatrans.models import KeyValue
from django.utils import translation

REGISTRY = []

class FieldDescriptor(object):
    def __init__(self, name):
        self.name = name

    def __get__(self, instance, owner):
        lang_code = translation.get_language()
        key = instance.__dict__[self.name]
        return KeyValue.objects.lookup(key, lang_code)

    def __set__(self, instance, value):
        instance.__dict__[self.name] = value

def register(model, modeltranslation):
    '''
    modeltranslation must be a class with the following attribute:

    fields = ('field1', 'field2', ...)

    For example:

    class BlogPostTranslation(object):
        fields = ('title', 'content',)

    '''

    REGISTRY.append((model, modeltranslation))
    for field in modeltranslation.fields:
        setattr(model, field, FieldDescriptor(field))


def make_messages():
    '''
    This function loops over all the registered models and, when necessary,
    creates KeyValue entries for the fields specified.
    '''
    object_count = 0

    for model, modeltranslation in REGISTRY:
        objects = model.objects.all()
        for object in objects:
            for field in modeltranslation.fields:
                for lang_code, lang_human in settings.LANGUAGES:
                    KeyValue.objects.lookup(object.__dict__[field], lang_code)
            object_count += 1

    print('%d objects processed.' % object_count)

