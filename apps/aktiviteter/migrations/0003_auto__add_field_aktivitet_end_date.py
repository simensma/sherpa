# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'Aktivitet.end_date'
        db.add_column('aktiviteter_aktivitet', 'end_date', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2013, 1, 15, 13, 12, 53, 472077)), keep_default=False)


    def backwards(self, orm):
        
        # Deleting field 'Aktivitet.end_date'
        db.delete_column('aktiviteter_aktivitet', 'end_date')


    models = {
        'aktiviteter.aktivitet': {
            'Meta': {'object_name': 'Aktivitet'},
            'description': ('django.db.models.fields.TextField', [], {}),
            'end_date': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'start_date': ('django.db.models.fields.DateTimeField', [], {}),
            'tags': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'aktiviteter'", 'symmetrical': 'False', 'to': "orm['core.Tag']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'core.tag': {
            'Meta': {'object_name': 'Tag'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        }
    }

    complete_apps = ['aktiviteter']
