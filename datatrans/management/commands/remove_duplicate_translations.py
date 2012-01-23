from collections import defaultdict

from django.core.management.base import BaseCommand

from datatrans.models import KeyValue


class Command(BaseCommand):
    def handle(self, *args, **options):
        kv_map = defaultdict(lambda: [])

        for kv in KeyValue.objects.all():
            key = (kv.language, kv.digest)
            kv_map[key].append(kv)

        for (language, digest), kv_list in kv_map.items():
            if len(kv_list) == 1:
                continue

            kv_list.sort(key=lambda kv: kv.id)

            for kv in kv_list[:-1]:
                print 'Deleting KeyValue', kv.id
                kv.delete()

