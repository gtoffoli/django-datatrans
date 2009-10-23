from django.db import models
from django.conf import settings

from hashlib import sha1

class KeyValueManager(models.Manager):
    def lookup(self, key, language):
        digest = sha1(key.encode('utf-8')).hexdigest()
        keyvalue, created = self.get_or_create(digest=digest, language=language, defaults={'value': key})
        return keyvalue.value


class KeyValue(models.Model):
    digest = models.CharField(max_length=40, db_index=True)
    language = models.CharField(max_length=5, db_index=True, choices=settings.LANGUAGES)
    value = models.TextField(blank=True)

    objects = KeyValueManager()

    def __unicode__(self):
        return u'%s: %s' % (self.language, self.value)

