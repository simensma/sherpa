# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    depends_on = (
        ("user", "0001_initial"),
    )

    def forwards(self, orm):
        
        # Adding model 'Image'
        db.create_table('admin_image', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('key', self.gf('django.db.models.fields.CharField')(max_length=8)),
            ('extension', self.gf('django.db.models.fields.CharField')(max_length=4)),
            ('hash', self.gf('django.db.models.fields.CharField')(max_length=40)),
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('album', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['admin.Album'])),
            ('photographer', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('credits', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('licence', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('exif', self.gf('django.db.models.fields.TextField')()),
            ('uploaded', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('uploader', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['user.Profile'])),
            ('width', self.gf('django.db.models.fields.IntegerField')()),
            ('height', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('admin', ['Image'])

        # Adding M2M table for field tags on 'Image'
        db.create_table('admin_image_tags', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('image', models.ForeignKey(orm['admin.image'], null=False)),
            ('tag', models.ForeignKey(orm['admin.tag'], null=False))
        ))
        db.create_unique('admin_image_tags', ['image_id', 'tag_id'])

        # Adding model 'Tag'
        db.create_table('admin_tag', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
        ))
        db.send_create_signal('admin', ['Tag'])

        # Adding model 'Album'
        db.create_table('admin_album', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('parent', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['admin.Album'], null=True)),
        ))
        db.send_create_signal('admin', ['Album'])

        # Adding model 'Keyword'
        db.create_table('admin_keyword', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('image', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['admin.Image'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
        ))
        db.send_create_signal('admin', ['Keyword'])


    def backwards(self, orm):
        
        # Deleting model 'Image'
        db.delete_table('admin_image')

        # Removing M2M table for field tags on 'Image'
        db.delete_table('admin_image_tags')

        # Deleting model 'Tag'
        db.delete_table('admin_tag')

        # Deleting model 'Album'
        db.delete_table('admin_album')

        # Deleting model 'Keyword'
        db.delete_table('admin_keyword')


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
            'credits': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'exif': ('django.db.models.fields.TextField', [], {}),
            'extension': ('django.db.models.fields.CharField', [], {'max_length': '4'}),
            'hash': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'height': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '8'}),
            'licence': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'photographer': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'tags': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'images'", 'symmetrical': 'False', 'to': "orm['admin.Tag']"}),
            'uploaded': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'uploader': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['user.Profile']"}),
            'width': ('django.db.models.fields.IntegerField', [], {})
        },
        'admin.keyword': {
            'Meta': {'object_name': 'Keyword'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['admin.Image']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'admin.tag': {
            'Meta': {'object_name': 'Tag'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
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
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2012, 8, 1, 16, 59, 20, 914775)'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2012, 8, 1, 16, 59, 20, 914602)'}),
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
        'user.profile': {
            'Meta': {'object_name': 'Profile'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'password_restore_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'password_restore_key': ('django.db.models.fields.CharField', [], {'max_length': '40', 'unique': 'True', 'null': 'True'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.User']", 'unique': 'True'})
        }
    }

    complete_apps = ['admin']
