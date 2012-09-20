# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    # Nothing to do - the model was manually moved between apps (admin to core)
    def forwards(self, orm):
        pass

    def backwards(self, orm):
        pass


    models = {
        'core.tag': {
            'Meta': {'object_name': 'Tag', 'db_table': "u'admin_tag'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        }
    }

    complete_apps = ['core']
