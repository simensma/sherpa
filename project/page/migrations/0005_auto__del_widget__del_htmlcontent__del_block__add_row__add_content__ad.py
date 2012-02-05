# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Deleting model 'Widget'
        db.delete_table('page_widget')

        # Deleting model 'HTMLContent'
        db.delete_table('page_htmlcontent')

        # Deleting model 'Block'
        db.delete_table('page_block')

        # Adding model 'Row'
        db.create_table('page_row', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('version', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['page.PageVersion'])),
            ('order', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('page', ['Row'])

        # Adding model 'Content'
        db.create_table('page_content', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('column', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['page.Column'])),
            ('content', self.gf('django.db.models.fields.TextField')()),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('order', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('page', ['Content'])

        # Adding model 'Column'
        db.create_table('page_column', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('row', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['page.Row'])),
            ('span', self.gf('django.db.models.fields.IntegerField')()),
            ('order', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('page', ['Column'])


    def backwards(self, orm):
        
        # Adding model 'Widget'
        db.create_table('page_widget', (
            ('widget', self.gf('django.db.models.fields.TextField')()),
            ('column', self.gf('django.db.models.fields.IntegerField')()),
            ('order', self.gf('django.db.models.fields.IntegerField')()),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('block', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['page.Block'])),
        ))
        db.send_create_signal('page', ['Widget'])

        # Adding model 'HTMLContent'
        db.create_table('page_htmlcontent', (
            ('column', self.gf('django.db.models.fields.IntegerField')()),
            ('order', self.gf('django.db.models.fields.IntegerField')()),
            ('content', self.gf('django.db.models.fields.TextField')()),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('block', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['page.Block'])),
        ))
        db.send_create_signal('page', ['HTMLContent'])

        # Adding model 'Block'
        db.create_table('page_block', (
            ('version', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['page.PageVersion'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('template', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('order', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('page', ['Block'])

        # Deleting model 'Row'
        db.delete_table('page_row')

        # Deleting model 'Content'
        db.delete_table('page_content')

        # Deleting model 'Column'
        db.delete_table('page_column')


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
        'page.pagevariant': {
            'Meta': {'object_name': 'PageVariant'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'page': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['page.Page']"}),
            'priority': ('django.db.models.fields.IntegerField', [], {}),
            'segment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['analytics.Segment']", 'null': 'True'}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'page.pageversion': {
            'Meta': {'object_name': 'PageVersion'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'variant': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['page.PageVariant']"}),
            'version': ('django.db.models.fields.IntegerField', [], {})
        },
        'page.row': {
            'Meta': {'object_name': 'Row'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'order': ('django.db.models.fields.IntegerField', [], {}),
            'version': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['page.PageVersion']"})
        }
    }

    complete_apps = ['page']
