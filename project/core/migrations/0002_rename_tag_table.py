# encoding: utf-8
import datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models, connection, transaction

class Migration(DataMigration):

    def forwards(self, orm):
        cursor = connection.cursor()
        cursor.execute("ALTER TABLE admin_tag RENAME TO core_tag")
        cursor.execute("ALTER SEQUENCE admin_tag_id_seq RENAME TO core_tag_id_seq")
        cursor.execute("UPDATE django_content_type SET app_label='core' WHERE name='tag'")
        transaction.commit_unless_managed()

    def backwards(self, orm):
        cursor = connection.cursor()
        cursor.execute("ALTER TABLE core_tag RENAME TO admin_tag")
        cursor.execute("ALTER SEQUENCE core_tag_id_seq RENAME TO admin_tag_id_seq")
        cursor.execute("UPDATE django_content_type SET app_label='admin' WHERE name='tag'")
        transaction.commit_unless_managed()


    models = {
        'core.tag': {
            'Meta': {'object_name': 'Tag'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        }
    }

    complete_apps = ['core']
