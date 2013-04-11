VERSION = (0, 1, 4)
# 1.3 is currently on pypi


def get_version():
    if len(VERSION) > 3 and VERSION[3] != 'final':
        return '%s.%s.%s %s' % (VERSION[0], VERSION[1], VERSION[2], VERSION[3])
    else:
        return '%s.%s.%s' % (VERSION[0], VERSION[1], VERSION[2])


__version__ = get_version()


def autodiscover():
    """
    Same principle as for importing the admin modules with autodiscover() from django.contrib.admin
    """
    import copy
    import logging
    from django.conf import settings
    from django.contrib.admin.sites import site
    from django.utils.importlib import import_module
    from django.utils.module_loading import module_has_submodule

    logger = logging.getLogger(__name__)

    for app in settings.INSTALLED_APPS:
        mod = import_module(app)
        before_import_registry = copy.copy(site._registry)

        try:
            import_module('%s.datatranslation' % app)
            logger.info("Imported %s.datatranslation" % app)
        except:
            site._registry = before_import_registry

            if module_has_submodule(mod, 'datatranslation'):
               raise SystemError('Oh snap, weird stuff going on. We detected a submodule called \'datatrans\' in %s' % app)


