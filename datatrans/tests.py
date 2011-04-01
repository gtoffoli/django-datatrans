from django.core.cache import cache
from django.test import TestCase
from django.utils import translation

from datatrans.models import KeyValue, make_digest


class DatatransTests(TestCase):
    def test_default_values(self):
        value_en = 'test_en'
        value_nl = 'test_nl'

        value = KeyValue.objects.lookup(value_en, 'nl')
        self.assertEqual(value, value_en)

        kv = KeyValue.objects.get_keyvalue(value_en, 'nl')
        kv.value = value_nl
        kv.save()

        value = KeyValue.objects.lookup(value_en, 'nl')
        self.assertEqual(value, value_en)

        kv.edited = True
        kv.save()

        value = KeyValue.objects.lookup(value_en, 'nl')
        self.assertEqual(value, value_nl)

    def test_cache(self):
        value_en = 'test_cache_en'
        value_nl = 'test_cache_nl'
        digest = make_digest(value_en)
        cache_key = 'datatrans_%s_%s' % ('nl', digest)

        self.assertEqual(cache.get(cache_key), None)

        translation.activate('nl')

        kv = KeyValue.objects.get_keyvalue(value_en, 'nl')
        self.assertEqual(cache.get(cache_key).value, value_en)
        kv.value = value_nl
        kv.save()
        kv = KeyValue.objects.get_keyvalue(value_en, 'nl')
        self.assertEqual(cache.get(cache_key).value, value_nl)
        kv.value = '%s2' % value_nl
        kv.save()
        self.assertEqual(cache.get(cache_key).value, '%s2' % value_nl)
        kv.delete()
        self.assertEqual(cache.get(cache_key), None)

    def test_fuzzy(self):
        value_en = 'test_en'
        value_nl = 'test_nl'

        kv = KeyValue.objects.get_keyvalue(value_en, 'nl')
        kv.value = value_nl
        kv.edited = True
        kv.fuzzy = True
        kv.save()

        value = KeyValue.objects.lookup(value_en, 'nl')
        self.assertEqual(value, value_nl)
