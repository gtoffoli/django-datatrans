from django.test import TestCase
from django.conf import settings
try:
    from django.db import DEFAULT_DB_ALIAS
except ImportError:
    pass
from django.utils import translation

from datatrans.models import KeyValue
from datatrans.utils import get_default_language

from test_project.testapp.models import Option
from test_project.testapp.utils import test_concurrently


if hasattr(settings, 'DATABASES'):
    DATABASE_ENGINE = settings.DATABASES[DEFAULT_DB_ALIAS]['ENGINE']
else:
    DATABASE_ENGINE = settings.DATABASE_ENGINE
USING_POSTGRESQL = DATABASE_ENGINE.startswith('postgresql') or \
    DATABASE_ENGINE.startswith('django.db.backends.postgresql')

class PostgresRegressionTest(TestCase):
    if USING_POSTGRESQL:
        def test_concurrent_inserts_with_same_value_break_pre_save(self):
            @test_concurrently(2)
            def add_new_records():
                value = "test string that does not already exist in db"
                option = Option(name=value)
                option.save()
                count_kv = KeyValue.objects.filter(language=get_default_language(),
                                                   value=value).count()
                self.assertEqual(count_kv, 1,
                                 u"Got %d KeyValues after concurrent insert instead of 1." % count_kv)
            add_new_records()

class RegressionTests(TestCase):
    def test_access_before_save_breaks_pre_save(self):
        translation.activate('en')
        value_en = "test1_en"
        option = Option(name=value_en)
        self.assertEqual(option.name, value_en)
        option.save()

        translation.activate('ro')
        self.assertEqual(option.name, value_en)
        value_ro = "test1_ro"
        option.name = value_ro
        self.assertEqual(option.name, value_ro)
        option.save()
        self.assertEqual(option.name, value_ro)

        translation.activate('en')
        value_en = "test2_en"
        option.name = value_en
        self.assertEqual(option.name, value_en) # this access causes the creation of a new KeyValue for 'en', which
                                                # causes the pre_save handler to skip creation of a new KeyValue for 'ro' language
                                                # and causes the last assertEqual to fail
        option.save()
        self.assertEqual(option.name, value_en)

        translation.activate('ro')
        self.assertEqual(option.name, value_ro)
