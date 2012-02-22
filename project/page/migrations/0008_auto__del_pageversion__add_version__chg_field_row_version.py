# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Deleting model 'PageVersion'
        db.delete_table('page_pageversion')

        # Adding model 'Version'
        db.create_table('page_version', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('variant', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['page.Variant'])),
            ('version', self.gf('django.db.models.fields.IntegerField')()),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('page', ['Version'])

        # Changing field 'Row.version'
        db.alter_column('page_row', 'version_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['page.Version']))


    def backwards(self, orm):
        
        # Adding model 'PageVersion'
        db.create_table('page_pageversion', (
            ('active', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('variant', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['page.Variant'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('version', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('page', ['PageVersion'])

        # Deleting model 'Version'
        db.delete_table('page_version')

        # Changing field 'Row.version'
        db.alter_column('page_row', 'version_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['page.PageVersion']))


    models = {
        'analytics.segment': {
            'Meta': {'object_name': 'Segment'},
            'description': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'page.column': {
            'Meta': {'object_name': 'Column'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'order': ('django.db.models.fields.IntegerField', [], {}),
            'row': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['page.Row']"}),
            'span': ('django.db.models.fields.IntegerField', [], {})
        },
        'page.content': {
            'Meta': {'object_name': 'Content'},
            'column': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['page.Column']"}),
            'content': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'order': ('django.db.models.fields.IntegerField', [], {}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '1'})
        },
        'page.menu': {
            'Meta': {'object_name': 'Menu'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'order': ('django.db.models.fields.IntegerField', [], {}),
            'page': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['page.Page']", 'unique': 'True'})
        },
        'page.page': {
            'Meta': {'object_name': 'Page'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'pub_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'published': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'slug': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'page.row': {
            'Meta': {'object_name': 'Row'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'order': ('django.db.models.fields.IntegerField', [], {}),
            'version': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['page.Version']"})
        },
        'page.variant': {
            'Meta': {'object_name': 'Variant'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'page': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['page.Page']"}),
            'priority': ('django.db.models.fields.IntegerField', [], {}),
            'segment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['analytics.Segment']", 'null': 'True'})
        },
        'page.version': {
            'Meta': {'object_name': 'Version'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'variant': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['page.Variant']"}),
            'version': ('django.db.models.fields.IntegerField', [], {})
        }
    }

    complete_apps = ['page']
