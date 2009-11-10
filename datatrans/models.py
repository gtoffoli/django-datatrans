from django.db import models
from django.conf import settings

from hashlib import sha1

def make_digest(key):
    return sha1(key.encode('utf-8')).hexdigest()

class KeyValueManager(models.Manager):
    def get_keyvalue(self, key, language):
        digest = make_digest(key)
        keyvalue, created = self.get_or_create(digest=digest, language=language, defaults={'value': key})
        return keyvalue

    def lookup(self, key, language):
        kv = self.get_keyvalue(key, language)
        if kv.edited:
            return kv.value
        else:
            return key

    def for_model(self, model, fields, modelfield=None):
        '''
        Get KeyValues for a model. The fields argument is a list of model fields.
        If modelfield is specified, only KeyValue entries for that field will be returned.
        '''
        objects = model.objects.all()
        digests = []

        for object in objects:
            if modelfield is None:
                for field in fields:
                    digests.append(make_digest(object.__dict__[field.name]))
            else:
                digests.append(make_digest(object.__dict__[modelfield]))

        return self.filter(digest__in=digests)


class KeyValue(models.Model):
    digest = models.CharField(max_length=40, db_index=True)
    language = models.CharField(max_length=5, db_index=True, choices=settings.LANGUAGES)
    value = models.TextField(blank=True)
    edited = models.BooleanField(blank=True, default=False)
    fuzzy = models.BooleanField(blank=True, default=False)

    objects = KeyValueManager()

    def __unicode__(self):
        return u'%s: %s' % (self.language, self.value)


