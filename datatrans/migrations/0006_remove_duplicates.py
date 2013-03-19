# -*- coding: utf-8 -*-
from collections import defaultdict
from django.db import connection, transaction
from south.db import db
from south.v2 import SchemaMigration


class Migration(SchemaMigration):

    @transaction.commit_on_success
    def remove_duplicates_mysql(self):
        """
        Removes all the duplicates from the datatrans_keyvalue table. First we detect what the most horrible
        duplication count is of a KeyValue.  Then we iterate through the count and start deleting the newest duplicate
        row of a certain KeyValue.  Wow, confused?

        The majority of KeyValues have 1 duplication, but some have 2 duplications. This means that we have to execute
        the deletion query twice since it only deletes 1 duplication (the newest) each time
        """
        print "  Deleting duplicates from datatrans_keyvalue table"
        cursor = connection.cursor()
        cursor.execute("""
            select count(id)
            from datatrans_keyvalue
            group by digest, language, content_type_id, object_id, field
            having count(*) > 1
            order by count(id) desc
        """)
        row = cursor.fetchone()

        if row and row[0] > 0:
            count = row[0]
            print "   - Most horrible duplication count = ", count

            for i in range(count - 1):
                # Mysql doesn't allow to delete in a table while fetching values from it (makes sense).
                # Therefore we have to fetch the duplicate ids first into a python list.
                # Secondly we pass this list to the deletion query
                print "   - Deleting entries with %s duplicates" % (i + 1)
                cursor.execute("""
                        select max(id)
                        from datatrans_keyvalue
                        group by digest, language, content_type_id, object_id, field
                        having count(*) > 1
                    """)

                ids = [str(_row[0]) for _row in cursor.fetchall()]
                strids = ",".join(ids)

                cursor.execute("""
                    delete from datatrans_keyvalue
                    where id in (%s)
                """ % strids)
        else:
            print "   - No duplicates found"

    def remove_duplicates_default(self, orm):
        """
        A cleaner implementation, but its way more slower slower

        @param orm:
        """
        kv_map = defaultdict(lambda: [])
        deleted = 0

        for kv in orm.KeyValue.objects.all():
            # For some reason a null object exists in the database
            if not kv.id:
                continue

            key = (kv.language, kv.digest, kv.content_type, kv.object_id, kv.field)
            kv_map[key].append(kv)

            for (kv.language, kv.digest, kv.content_type, kv.object_id, kv.field), kv_list in kv_map.items():
                if len(kv_list) == 1:
                    continue

                kv_list.sort(key=lambda kv: kv.id)

                for kv in kv_list[:-1]:
                    if kv.id:
                        print 'Deleting KeyValue', kv.id, ", ", str(kv)
                        deleted += 1
                        kv.delete()

        print "Duplicates deleted: ", deleted

    def forwards(self, orm):
        # First we delete duplicate entries before we can create the new unique index
        if not db.dry_run:
            if db.backend_name == 'mysql':
                print "Remove duplicates: mysql"
                self.remove_duplicates_mysql()
            else:
                print "Remove duplicates: default"
                self.remove_duplicates_default(orm)
        else:
            print "Dry running deletion of duplicates"

    def backwards(self, orm):
        pass

    models = {
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'datatrans.fieldwordcount': {
            'Meta': {'unique_together': "(('content_type', 'field'),)", 'object_name': 'FieldWordCount'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'field': ('django.db.models.fields.CharField', [], {'max_length': '64', 'db_index': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'total_words': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'valid': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'datatrans.keyvalue': {
            'Meta': {'unique_together': "(('digest', 'language'),)", 'object_name': 'KeyValue'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']", 'null': 'True'}),
            'digest': ('django.db.models.fields.CharField', [], {'max_length': '40', 'db_index': 'True'}),
            'edited': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'field': ('django.db.models.fields.TextField', [], {}),
            'fuzzy': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.CharField', [], {'max_length': '5', 'db_index': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {'default': 'None', 'null': 'True'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True'}),
            'value': ('django.db.models.fields.TextField', [], {'blank': 'True'})
        },
        'datatrans.modelwordcount': {
            'Meta': {'object_name': 'ModelWordCount'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']", 'unique': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'total_words': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'valid': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        }
    }

    complete_apps = ['datatrans']