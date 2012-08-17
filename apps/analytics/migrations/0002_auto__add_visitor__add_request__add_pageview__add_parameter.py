# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    depends_on = (
        ("user", "0001_initial"),
        ("page", "0001_initial"),
    )

    def forwards(self, orm):
        
        # Adding model 'Visitor'
        db.create_table('analytics_visitor', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('profile', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['user.Profile'], unique=True, null=True)),
        ))
        db.send_create_signal('analytics', ['Visitor'])

        # Adding model 'Request'
        db.create_table('analytics_request', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('visitor', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['analytics.Visitor'])),
            ('http_method', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('path', self.gf('django.db.models.fields.CharField')(max_length=2048)),
            ('server_host', self.gf('django.db.models.fields.CharField')(max_length=2048)),
            ('client_ip', self.gf('django.db.models.fields.CharField')(max_length=39)),
            ('client_host', self.gf('django.db.models.fields.CharField')(max_length=2048)),
            ('referrer', self.gf('django.db.models.fields.CharField')(max_length=2048)),
            ('enter', self.gf('django.db.models.fields.DateTimeField')()),
            ('ajax', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('analytics', ['Request'])

        # Adding model 'Pageview'
        db.create_table('analytics_pageview', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('request', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['analytics.Request'], unique=True)),
            ('variant', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['page.Variant'])),
            ('active_version', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['page.Version'])),
            ('requested_segment', self.gf('django.db.models.fields.related.ForeignKey')(related_name='requested', null=True, to=orm['analytics.Segment'])),
            ('matched_segment', self.gf('django.db.models.fields.related.ForeignKey')(related_name='matched', null=True, to=orm['analytics.Segment'])),
        ))
        db.send_create_signal('analytics', ['Pageview'])

        # Adding model 'Parameter'
        db.create_table('analytics_parameter', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('request', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['analytics.Request'])),
            ('key', self.gf('django.db.models.fields.TextField')()),
            ('value', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('analytics', ['Parameter'])


    def backwards(self, orm):
        
        # Deleting model 'Visitor'
        db.delete_table('analytics_visitor')

        # Deleting model 'Request'
        db.delete_table('analytics_request')

        # Deleting model 'Pageview'
        db.delete_table('analytics_pageview')

        # Deleting model 'Parameter'
        db.delete_table('analytics_parameter')


    models = {
        'analytics.pageview': {
            'Meta': {'object_name': 'Pageview'},
            'active_version': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['page.Version']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'matched_segment': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'matched'", 'null': 'True', 'to': "orm['analytics.Segment']"}),
            'request': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['analytics.Request']", 'unique': 'True'}),
            'requested_segment': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'requested'", 'null': 'True', 'to': "orm['analytics.Segment']"}),
            'variant': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['page.Variant']"})
        },
        'analytics.parameter': {
            'Meta': {'object_name': 'Parameter'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.TextField', [], {}),
            'request': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['analytics.Request']"}),
            'value': ('django.db.models.fields.TextField', [], {})
        },
        'analytics.request': {
            'Meta': {'object_name': 'Request'},
            'ajax': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'client_host': ('django.db.models.fields.CharField', [], {'max_length': '2048'}),
            'client_ip': ('django.db.models.fields.CharField', [], {'max_length': '39'}),
            'enter': ('django.db.models.fields.DateTimeField', [], {}),
            'http_method': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'path': ('django.db.models.fields.CharField', [], {'max_length': '2048'}),
            'referrer': ('django.db.models.fields.CharField', [], {'max_length': '2048'}),
            'server_host': ('django.db.models.fields.CharField', [], {'max_length': '2048'}),
            'visitor': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['analytics.Visitor']"})
        },
        'analytics.segment': {
            'Meta': {'object_name': 'Segment'},
            'description': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'analytics.visitor': {
            'Meta': {'object_name': 'Visitor'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'profile': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['user.Profile']", 'unique': 'True', 'null': 'True'})
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
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2012, 8, 1, 16, 59, 10, 995542)'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2012, 8, 1, 16, 59, 10, 995242)'}),
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

    complete_apps = ['analytics']
