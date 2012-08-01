# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    depends_on = (
        ("user", "0021_auto__del_field_zipcode_zip_code"),
    )

    def forwards(self, orm):
        
        # Adding model 'Keyword'
        db.create_table('admin_keyword', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('image', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['admin.Image'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
        ))
        db.send_create_signal('admin', ['Keyword'])

        # Deleting field 'Image.position'
        db.delete_column('admin_image', 'position')

        # Adding field 'Image.photographer'
        db.add_column('admin_image', 'photographer', self.gf('django.db.models.fields.CharField')(default='', max_length=200), keep_default=False)

        # Adding field 'Image.credits'
        db.add_column('admin_image', 'credits', self.gf('django.db.models.fields.CharField')(default='', max_length=20), keep_default=False)

        # Adding field 'Image.photographer_contact'
        db.add_column('admin_image', 'photographer_contact', self.gf('django.db.models.fields.CharField')(default='', max_length=200), keep_default=False)

        # Adding field 'Image.uploaded'
        db.add_column('admin_image', 'uploaded', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, default=datetime.datetime(2012, 1, 31, 10, 32, 38, 765255), blank=True), keep_default=False)

        # Adding field 'Image.uploader'
        db.add_column('admin_image', 'uploader', self.gf('django.db.models.fields.related.ForeignKey')(default=0, to=orm['user.Profile']), keep_default=False)

        # Adding field 'Image.height'
        db.add_column('admin_image', 'height', self.gf('django.db.models.fields.IntegerField')(default=0), keep_default=False)

        # Adding field 'Image.width'
        db.add_column('admin_image', 'width', self.gf('django.db.models.fields.IntegerField')(default=0), keep_default=False)


    def backwards(self, orm):
        
        # Deleting model 'Keyword'
        db.delete_table('admin_keyword')

        # Adding field 'Image.position'
        db.add_column('admin_image', 'position', self.gf('django.db.models.fields.IntegerField')(default=0, unique=True), keep_default=False)

        # Deleting field 'Image.photographer'
        db.delete_column('admin_image', 'photographer')

        # Deleting field 'Image.credits'
        db.delete_column('admin_image', 'credits')

        # Deleting field 'Image.photographer_contact'
        db.delete_column('admin_image', 'photographer_contact')

        # Deleting field 'Image.uploaded'
        db.delete_column('admin_image', 'uploaded')

        # Deleting field 'Image.uploader'
        db.delete_column('admin_image', 'uploader_id')

        # Deleting field 'Image.height'
        db.delete_column('admin_image', 'height')

        # Deleting field 'Image.width'
        db.delete_column('admin_image', 'width')


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
            'credits': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'hash': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'height': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'photographer': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'photographer_contact': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
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
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
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
            'text': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.User']", 'unique': 'True'})
        }
    }

    complete_apps = ['admin']
