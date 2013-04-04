# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'AktivitetDate'
        db.create_table('aktiviteter_aktivitetdate', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('aktivitet', self.gf('django.db.models.fields.related.ForeignKey')(related_name='dates', to=orm['aktiviteter.Aktivitet'])),
            ('start_date', self.gf('django.db.models.fields.DateTimeField')()),
            ('end_date', self.gf('django.db.models.fields.DateTimeField')()),
            ('signup_enabled', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('signup_start', self.gf('django.db.models.fields.DateField')()),
            ('signup_deadline', self.gf('django.db.models.fields.DateField')()),
            ('signup_cancel_deadline', self.gf('django.db.models.fields.DateField')()),
        ))
        db.send_create_signal('aktiviteter', ['AktivitetDate'])

        # Adding M2M table for field participants on 'AktivitetDate'
        db.create_table('aktiviteter_aktivitetdate_participants', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('aktivitetdate', models.ForeignKey(orm['aktiviteter.aktivitetdate'], null=False)),
            ('profile', models.ForeignKey(orm['user.profile'], null=False))
        ))
        db.create_unique('aktiviteter_aktivitetdate_participants', ['aktivitetdate_id', 'profile_id'])

        # Deleting field 'Aktivitet.end_date'
        db.delete_column('aktiviteter_aktivitet', 'end_date')

        # Deleting field 'Aktivitet.signup_deadline'
        db.delete_column('aktiviteter_aktivitet', 'signup_deadline')

        # Deleting field 'Aktivitet.signup_cancel_deadline'
        db.delete_column('aktiviteter_aktivitet', 'signup_cancel_deadline')

        # Deleting field 'Aktivitet.signup_enabled'
        db.delete_column('aktiviteter_aktivitet', 'signup_enabled')

        # Deleting field 'Aktivitet.start_date'
        db.delete_column('aktiviteter_aktivitet', 'start_date')

        # Deleting field 'Aktivitet.signup_start'
        db.delete_column('aktiviteter_aktivitet', 'signup_start')

        # Removing M2M table for field participants on 'Aktivitet'
        db.delete_table('aktiviteter_aktivitet_participants')


    def backwards(self, orm):
        # Deleting model 'AktivitetDate'
        db.delete_table('aktiviteter_aktivitetdate')

        # Removing M2M table for field participants on 'AktivitetDate'
        db.delete_table('aktiviteter_aktivitetdate_participants')


        # User chose to not deal with backwards NULL issues for 'Aktivitet.end_date'
        raise RuntimeError("Cannot reverse this migration. 'Aktivitet.end_date' and its values cannot be restored.")

        # User chose to not deal with backwards NULL issues for 'Aktivitet.signup_deadline'
        raise RuntimeError("Cannot reverse this migration. 'Aktivitet.signup_deadline' and its values cannot be restored.")

        # User chose to not deal with backwards NULL issues for 'Aktivitet.signup_cancel_deadline'
        raise RuntimeError("Cannot reverse this migration. 'Aktivitet.signup_cancel_deadline' and its values cannot be restored.")
        # Adding field 'Aktivitet.signup_enabled'
        db.add_column('aktiviteter_aktivitet', 'signup_enabled',
                      self.gf('django.db.models.fields.BooleanField')(default=True),
                      keep_default=False)


        # User chose to not deal with backwards NULL issues for 'Aktivitet.start_date'
        raise RuntimeError("Cannot reverse this migration. 'Aktivitet.start_date' and its values cannot be restored.")

        # User chose to not deal with backwards NULL issues for 'Aktivitet.signup_start'
        raise RuntimeError("Cannot reverse this migration. 'Aktivitet.signup_start' and its values cannot be restored.")
        # Adding M2M table for field participants on 'Aktivitet'
        db.create_table('aktiviteter_aktivitet_participants', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('aktivitet', models.ForeignKey(orm['aktiviteter.aktivitet'], null=False)),
            ('profile', models.ForeignKey(orm['user.profile'], null=False))
        ))
        db.create_unique('aktiviteter_aktivitet_participants', ['aktivitet_id', 'profile_id'])


    models = {
        'aktiviteter.aktivitet': {
            'Meta': {'object_name': 'Aktivitet'},
            'description': ('django.db.models.fields.TextField', [], {}),
            'hidden': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'pub_date': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'tags': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'aktiviteter'", 'symmetrical': 'False', 'to': "orm['core.Tag']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'aktiviteter.aktivitetdate': {
            'Meta': {'object_name': 'AktivitetDate'},
            'aktivitet': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'dates'", 'to': "orm['aktiviteter.Aktivitet']"}),
            'end_date': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'participants': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'aktiviteter'", 'symmetrical': 'False', 'to': "orm['user.Profile']"}),
            'signup_cancel_deadline': ('django.db.models.fields.DateField', [], {}),
            'signup_deadline': ('django.db.models.fields.DateField', [], {}),
            'signup_enabled': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'signup_start': ('django.db.models.fields.DateField', [], {}),
            'start_date': ('django.db.models.fields.DateTimeField', [], {})
        },
        'association.association': {
            'Meta': {'object_name': 'Association'},
            'counties': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'associations'", 'symmetrical': 'False', 'to': "orm['core.County']"}),
            'email': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255'}),
            'facebook_url': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '2048'}),
            'focus_id': ('django.db.models.fields.IntegerField', [], {'default': 'None', 'null': 'True'}),
            'gmap_url': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '2048'}),
            'group_type': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'organization_no': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'children'", 'null': 'True', 'to': "orm['association.Association']"}),
            'phone': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255'}),
            'post_address': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255'}),
            'site': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['core.Site']", 'unique': 'True', 'null': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'visit_address': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255'}),
            'zipcode': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Zipcode']", 'null': 'True'})
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
        'core.county': {
            'Meta': {'object_name': 'County'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'core.site': {
            'Meta': {'object_name': 'Site'},
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'prefix': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'template': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.SiteTemplate']"})
        },
        'core.sitetemplate': {
            'Meta': {'object_name': 'SiteTemplate'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'core.tag': {
            'Meta': {'object_name': 'Tag'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'core.zipcode': {
            'Meta': {'object_name': 'Zipcode'},
            'area': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'city_code': ('django.db.models.fields.CharField', [], {'max_length': '4'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'zipcode': ('django.db.models.fields.CharField', [], {'max_length': '4'})
        },
        'user.associationrole': {
            'Meta': {'object_name': 'AssociationRole'},
            'association': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['association.Association']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'profile': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['user.Profile']"}),
            'role': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'user.profile': {
            'Meta': {'object_name': 'Profile'},
            'associations': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'users'", 'symmetrical': 'False', 'through': "orm['user.AssociationRole']", 'to': "orm['association.Association']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'memberid': ('django.db.models.fields.IntegerField', [], {'unique': 'True', 'null': 'True'}),
            'password_restore_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'password_restore_key': ('django.db.models.fields.CharField', [], {'max_length': '40', 'null': 'True'}),
            'sherpa_email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.User']", 'unique': 'True'})
        }
    }

    complete_apps = ['aktiviteter']