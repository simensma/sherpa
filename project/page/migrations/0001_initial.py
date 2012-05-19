# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    depends_on = (
        ("analytics", "0001_initial__segment"),
    )

    def forwards(self, orm):
        
        # Adding model 'Menu'
        db.create_table('page_menu', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('page', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['page.Page'], unique=True)),
            ('position', self.gf('django.db.models.fields.IntegerField')(unique=True)),
        ))
        db.send_create_signal('page', ['Menu'])

        # Adding model 'Page'
        db.create_table('page_page', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('slug', self.gf('django.db.models.fields.CharField')(unique=True, max_length=50)),
            ('published', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('pub_date', self.gf('django.db.models.fields.DateTimeField')(null=True)),
        ))
        db.send_create_signal('page', ['Page'])

        # Adding model 'PageVariant'
        db.create_table('page_pagevariant', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('page', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['page.Page'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('slug', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('segment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['analytics.Segment'], null=True)),
            ('priority', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('page', ['PageVariant'])

        # Adding model 'PageVersion'
        db.create_table('page_pageversion', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('variant', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['page.PageVariant'])),
            ('version', self.gf('django.db.models.fields.IntegerField')()),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('page', ['PageVersion'])

        # Adding model 'Block'
        db.create_table('page_block', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('version', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['page.PageVersion'])),
            ('template', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('order', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('page', ['Block'])

        # Adding model 'HTMLContent'
        db.create_table('page_htmlcontent', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('block', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['page.Block'])),
            ('content', self.gf('django.db.models.fields.TextField')()),
            ('column', self.gf('django.db.models.fields.IntegerField')()),
            ('order', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('page', ['HTMLContent'])

        # Adding model 'Widget'
        db.create_table('page_widget', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('block', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['page.Block'])),
            ('widget', self.gf('django.db.models.fields.TextField')()),
            ('column', self.gf('django.db.models.fields.IntegerField')()),
            ('order', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('page', ['Widget'])


    def backwards(self, orm):
        
        # Deleting model 'Menu'
        db.delete_table('page_menu')

        # Deleting model 'Page'
        db.delete_table('page_page')

        # Deleting model 'PageVariant'
        db.delete_table('page_pagevariant')

        # Deleting model 'PageVersion'
        db.delete_table('page_pageversion')

        # Deleting model 'Block'
        db.delete_table('page_block')

        # Deleting model 'HTMLContent'
        db.delete_table('page_htmlcontent')

        # Deleting model 'Widget'
        db.delete_table('page_widget')


    models = {
        'analytics.segment': {
            'Meta': {'object_name': 'Segment'},
            'description': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'page.block': {
            'Meta': {'object_name': 'Block'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'order': ('django.db.models.fields.IntegerField', [], {}),
            'template': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'version': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['page.PageVersion']"})
        },
        'page.htmlcontent': {
            'Meta': {'object_name': 'HTMLContent'},
            'block': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['page.Block']"}),
            'column': ('django.db.models.fields.IntegerField', [], {}),
            'content': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'order': ('django.db.models.fields.IntegerField', [], {})
        },
        'page.menu': {
            'Meta': {'object_name': 'Menu'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'page': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['page.Page']", 'unique': 'True'}),
            'position': ('django.db.models.fields.IntegerField', [], {'unique': 'True'})
        },
        'page.page': {
            'Meta': {'object_name': 'Page'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'pub_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'published': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'slug': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'})
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
        'page.widget': {
            'Meta': {'object_name': 'Widget'},
            'block': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['page.Block']"}),
            'column': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'order': ('django.db.models.fields.IntegerField', [], {}),
            'widget': ('django.db.models.fields.TextField', [], {})
        }
    }

    complete_apps = ['page']
