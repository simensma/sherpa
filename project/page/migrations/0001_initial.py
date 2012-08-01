# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    depends_on = (
        ("user", "0001_initial"),
        ("analytics", "0001_initial"),
        ("articles", "0001_initial"),
    )

    def forwards(self, orm):
        
        # Adding model 'Menu'
        db.create_table('page_menu', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('url', self.gf('django.db.models.fields.CharField')(max_length=2048)),
            ('order', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('page', ['Menu'])

        # Adding model 'Page'
        db.create_table('page_page', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('slug', self.gf('django.db.models.fields.CharField')(unique=True, max_length=50)),
            ('published', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('pub_date', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('publisher', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['user.Profile'])),
        ))
        db.send_create_signal('page', ['Page'])

        # Adding model 'Variant'
        db.create_table('page_variant', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('page', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['page.Page'], null=True)),
            ('article', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['articles.Article'], null=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('segment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['analytics.Segment'], null=True)),
            ('priority', self.gf('django.db.models.fields.IntegerField')()),
            ('publisher', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['user.Profile'])),
        ))
        db.send_create_signal('page', ['Variant'])

        # Adding model 'Version'
        db.create_table('page_version', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('variant', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['page.Variant'])),
            ('version', self.gf('django.db.models.fields.IntegerField')()),
            ('publisher', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['user.Profile'])),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('page', ['Version'])

        # Adding model 'Row'
        db.create_table('page_row', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('version', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['page.Version'])),
            ('order', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('page', ['Row'])

        # Adding model 'Column'
        db.create_table('page_column', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('row', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['page.Row'])),
            ('span', self.gf('django.db.models.fields.IntegerField')()),
            ('offset', self.gf('django.db.models.fields.IntegerField')()),
            ('order', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('page', ['Column'])

        # Adding model 'Content'
        db.create_table('page_content', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('column', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['page.Column'])),
            ('content', self.gf('django.db.models.fields.TextField')()),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('order', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('page', ['Content'])

        # Adding model 'Ad'
        db.create_table('page_ad', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('extension', self.gf('django.db.models.fields.CharField')(max_length=4)),
            ('destination', self.gf('django.db.models.fields.CharField')(max_length=2048)),
            ('sha1_hash', self.gf('django.db.models.fields.CharField')(max_length=40)),
            ('content_type', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('width', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('height', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('fallback_extension', self.gf('django.db.models.fields.CharField')(max_length=4, null=True)),
            ('fallback_sha1_hash', self.gf('django.db.models.fields.CharField')(max_length=40, null=True)),
            ('fallback_content_type', self.gf('django.db.models.fields.CharField')(max_length=200, null=True)),
        ))
        db.send_create_signal('page', ['Ad'])

        # Adding model 'AdPlacement'
        db.create_table('page_adplacement', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('ad', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['page.Ad'])),
            ('start_date', self.gf('django.db.models.fields.DateField')()),
            ('end_date', self.gf('django.db.models.fields.DateField')()),
            ('placement', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('views', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('clicks', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal('page', ['AdPlacement'])


    def backwards(self, orm):
        
        # Deleting model 'Menu'
        db.delete_table('page_menu')

        # Deleting model 'Page'
        db.delete_table('page_page')

        # Deleting model 'Variant'
        db.delete_table('page_variant')

        # Deleting model 'Version'
        db.delete_table('page_version')

        # Deleting model 'Row'
        db.delete_table('page_row')

        # Deleting model 'Column'
        db.delete_table('page_column')

        # Deleting model 'Content'
        db.delete_table('page_content')

        # Deleting model 'Ad'
        db.delete_table('page_ad')

        # Deleting model 'AdPlacement'
        db.delete_table('page_adplacement')


    models = {
        'analytics.segment': {
            'Meta': {'object_name': 'Segment'},
            'description': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'articles.article': {
            'Meta': {'object_name': 'Article'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'hide_thumbnail': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'pub_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'published': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'publisher': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['user.Profile']"}),
            'thumbnail': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True'})
        },
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2012, 8, 1, 16, 59, 25, 572750)'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2012, 8, 1, 16, 59, 25, 572582)'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'page.ad': {
            'Meta': {'object_name': 'Ad'},
            'content_type': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'destination': ('django.db.models.fields.CharField', [], {'max_length': '2048'}),
            'extension': ('django.db.models.fields.CharField', [], {'max_length': '4'}),
            'fallback_content_type': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True'}),
            'fallback_extension': ('django.db.models.fields.CharField', [], {'max_length': '4', 'null': 'True'}),
            'fallback_sha1_hash': ('django.db.models.fields.CharField', [], {'max_length': '40', 'null': 'True'}),
            'height': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'sha1_hash': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'width': ('django.db.models.fields.IntegerField', [], {'null': 'True'})
        },
        'page.adplacement': {
            'Meta': {'object_name': 'AdPlacement'},
            'ad': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['page.Ad']"}),
            'clicks': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'end_date': ('django.db.models.fields.DateField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'placement': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'start_date': ('django.db.models.fields.DateField', [], {}),
            'views': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'page.column': {
            'Meta': {'object_name': 'Column'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'offset': ('django.db.models.fields.IntegerField', [], {}),
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
            'type': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'page.menu': {
            'Meta': {'object_name': 'Menu'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'order': ('django.db.models.fields.IntegerField', [], {}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '2048'})
        },
        'page.page': {
            'Meta': {'object_name': 'Page'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'pub_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'published': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'publisher': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['user.Profile']"}),
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
            'article': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['articles.Article']", 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'page': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['page.Page']", 'null': 'True'}),
            'priority': ('django.db.models.fields.IntegerField', [], {}),
            'publisher': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['user.Profile']"}),
            'segment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['analytics.Segment']", 'null': 'True'})
        },
        'page.version': {
            'Meta': {'object_name': 'Version'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'publisher': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['user.Profile']"}),
            'variant': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['page.Variant']"}),
            'version': ('django.db.models.fields.IntegerField', [], {})
        },
        'user.profile': {
            'Meta': {'object_name': 'Profile'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'password_restore_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'password_restore_key': ('django.db.models.fields.CharField', [], {'max_length': '40', 'unique': 'True', 'null': 'True'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.User']", 'unique': 'True'})
        }
    }

    complete_apps = ['page']
