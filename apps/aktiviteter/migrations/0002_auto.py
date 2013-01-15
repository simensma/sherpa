# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding M2M table for field tags on 'Aktivitet'
        db.create_table('aktiviteter_aktivitet_tags', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('aktivitet', models.ForeignKey(orm['aktiviteter.aktivitet'], null=False)),
            ('tag', models.ForeignKey(orm['core.tag'], null=False))
        ))
        db.create_unique('aktiviteter_aktivitet_tags', ['aktivitet_id', 'tag_id'])


    def backwards(self, orm):
        
        # Removing M2M table for field tags on 'Aktivitet'
        db.delete_table('aktiviteter_aktivitet_tags')


    models = {
        'aktiviteter.aktivitet': {
            'Meta': {'object_name': 'Aktivitet'},
            'description': ('django.db.models.fields.TextField', [], {}),
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
