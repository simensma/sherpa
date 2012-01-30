# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Image'
        db.create_table('admin_image', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('hash', self.gf('django.db.models.fields.CharField')(max_length=40)),
            ('album', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['admin.Album'])),
            ('position', self.gf('django.db.models.fields.IntegerField')(unique=True)),
        ))
        db.send_create_signal('admin', ['Image'])

        # Adding model 'Album'
        db.create_table('admin_album', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('parent', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['admin.Album'], null=True)),
        ))
        db.send_create_signal('admin', ['Album'])


    def backwards(self, orm):
        
        # Deleting model 'Image'
        db.delete_table('admin_image')

        # Deleting model 'Album'
        db.delete_table('admin_album')


    models = {
        'admin.album': {
            'Meta': {'object_name': 'Album'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['admin.Album']", 'null': 'True'})
        },
        'admin.image': {
            'Meta': {'object_name': 'Image'},
            'album': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['admin.Album']"}),
            'hash': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'position': ('django.db.models.fields.IntegerField', [], {'unique': 'True'})
        }
    }

    complete_apps = ['admin']
