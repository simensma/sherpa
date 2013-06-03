# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Aktivitet'
        db.create_table('aktiviteter_aktivitet', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('start_date', self.gf('django.db.models.fields.DateTimeField')()),
        ))
        db.send_create_signal('aktiviteter', ['Aktivitet'])


    def backwards(self, orm):
        
        # Deleting model 'Aktivitet'
        db.delete_table('aktiviteter_aktivitet')


    models = {
        'aktiviteter.aktivitet': {
            'Meta': {'object_name': 'Aktivitet'},
            'description': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'start_date': ('django.db.models.fields.DateTimeField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        }
    }

    complete_apps = ['aktiviteter']
