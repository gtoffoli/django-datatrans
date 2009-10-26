from django.db import models
from django.conf import settings

from hashlib import sha1


class KeyValueManager(models.Manager):
    def get_keyvalue(self, key, language):
        digest = sha1(key.encode('utf-8')).hexdigest()
        keyvalue, created = self.get_or_create(digest=digest, language=language, defaults={'value': key})
        return keyvalue

    def lookup(self, key, language):
        return self.get_keyvalue(key, language).value

    def for_model(self, model, modeltranslation, modelfield=None):
        objects = model.objects.all()
        digests = []

        for object in objects:
            if modelfield is None:
                for field in modeltranslation.fields:
                    digests.append(sha1(object.__dict__[field].encode('utf-8')).hexdigest())
            else:
                digests.append(sha1(object.__dict__[modelfield].encode('utf-8')).hexdigest())

        return self.filter(digest__in=digests)


class KeyValue(models.Model):
    digest = models.CharField(max_length=40, db_index=True)
    language = models.CharField(max_length=5, db_index=True, choices=settings.LANGUAGES)
    value = models.TextField(blank=True)
    edited = models.BooleanField(blank=True, default=False)

    objects = KeyValueManager()

    def __unicode__(self):
        return u'%s: %s' % (self.language, self.value)


