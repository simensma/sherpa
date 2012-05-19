# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    depends_on = (
        ("analytics", "0002_initial__rest"),
    )

    def forwards(self, orm):
        
        # Deleting model 'PageVariant'
        db.delete_table('page_pagevariant')

        # Adding model 'Variant'
        db.create_table('page_variant', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('page', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['page.Page'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('segment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['analytics.Segment'], null=True)),
            ('priority', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('page', ['Variant'])

        # Changing field 'PageVersion.variant'
        db.alter_column('page_pageversion', 'variant_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['page.Variant']))


    def backwards(self, orm):
        
        # Adding model 'PageVariant'
        db.create_table('page_pagevariant', (
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('page', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['page.Page'])),
            ('priority', self.gf('django.db.models.fields.IntegerField')()),
            ('segment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['analytics.Segment'], null=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('page', ['PageVariant'])

        # Deleting model 'Variant'
        db.delete_table('page_variant')

        # Changing field 'PageVersion.variant'
        db.alter_column('page_pageversion', 'variant_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['page.PageVariant']))


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
        'page.pageversion': {
            'Meta': {'object_name': 'PageVersion'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'variant': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['page.Variant']"}),
            'version': ('django.db.models.fields.IntegerField', [], {})
        },
        'page.row': {
            'Meta': {'object_name': 'Row'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'order': ('django.db.models.fields.IntegerField', [], {}),
            'version': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['page.PageVersion']"})
        },
        'page.variant': {
            'Meta': {'object_name': 'Variant'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'page': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['page.Page']"}),
            'priority': ('django.db.models.fields.IntegerField', [], {}),
            'segment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['analytics.Segment']", 'null': 'True'})
        }
    }

    complete_apps = ['page']
