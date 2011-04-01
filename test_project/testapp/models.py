from django.db import models
from django.utils.translation import ugettext_lazy as _
from datatrans.utils import register

# Create your models here.
class Option(models.Model):
    name = models.CharField(_(u'name'), max_length=64)

    class Meta:
        verbose_name = _(u'option')
        verbose_name_plural = _(u'options')

    def __unicode__(self):
        return u'%s' % self.name

# register translations
class OptionTranslation(object):
    fields = ('name',)

register(Option, OptionTranslation)
