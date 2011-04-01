from django.db import models
from django.utils.translation import ugettext as _
from datatrans.utils import register

# Create your models here.
class Option(models.Model):
    name = models.CharField(_("name"), max_length=64)
    
    class Meta:
        verbose_name = _("option")
        verbose_name_plural = _("options")
        
    def __unicode__(self):
        return u'%s' % self.name
    
# register translations
class OptionTranslation(object):
    fields = ('name',)
    
register(Option, OptionTranslation)