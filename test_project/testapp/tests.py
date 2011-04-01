from django.test import TestCase
from django.conf import settings
try:
    from django.db import DEFAULT_DB_ALIAS
except ImportError:
    pass

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