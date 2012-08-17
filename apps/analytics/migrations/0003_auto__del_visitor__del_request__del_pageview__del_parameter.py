# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Deleting model 'Visitor'
        db.delete_table('analytics_visitor')

        # Deleting model 'Request'
        db.delete_table('analytics_request')

        # Deleting model 'Pageview'
        db.delete_table('analytics_pageview')

        # Deleting model 'Parameter'
        db.delete_table('analytics_parameter')


    def backwards(self, orm):
        
        # Adding model 'Visitor'
        db.create_table('analytics_visitor', (
            ('profile', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['user.Profile'], unique=True, null=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('analytics', ['Visitor'])

        # Adding model 'Request'
        db.create_table('analytics_request', (
            ('client_ip', self.gf('django.db.models.fields.CharField')(max_length=39)),
            ('visitor', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['analytics.Visitor'])),
            ('ajax', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('http_method', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('path', self.gf('django.db.models.fields.CharField')(max_length=2048)),
            ('client_host', self.gf('django.db.models.fields.CharField')(max_length=2048)),
            ('referrer', self.gf('django.db.models.fields.CharField')(max_length=2048)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('server_host', self.gf('django.db.models.fields.CharField')(max_length=2048)),
            ('enter', self.gf('django.db.models.fields.DateTimeField')()),
        ))
        db.send_create_signal('analytics', ['Request'])

        # Adding model 'Pageview'
        db.create_table('analytics_pageview', (
            ('requested_segment', self.gf('django.db.models.fields.related.ForeignKey')(related_name='requested', null=True, to=orm['analytics.Segment'])),
            ('variant', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['page.Variant'])),
            ('request', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['analytics.Request'], unique=True)),
            ('matched_segment', self.gf('django.db.models.fields.related.ForeignKey')(related_name='matched', null=True, to=orm['analytics.Segment'])),
            ('active_version', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['page.Version'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('analytics', ['Pageview'])

        # Adding model 'Parameter'
        db.create_table('analytics_parameter', (
            ('value', self.gf('django.db.models.fields.TextField')()),
            ('request', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['analytics.Request'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('key', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('analytics', ['Parameter'])


    models = {
        'analytics.segment': {
            'Meta': {'object_name': 'Segment'},
            'description': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        }
    }

    complete_apps = ['analytics']
