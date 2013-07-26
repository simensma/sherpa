# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'SimpleParticipant'
        db.create_table(u'aktiviteter_simpleparticipant', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('aktivitet_date', self.gf('django.db.models.fields.related.ForeignKey')(related_name='simple_participants', to=orm['aktiviteter.AktivitetDate'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('email', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('phone', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal(u'aktiviteter', ['SimpleParticipant'])


    def backwards(self, orm):
        # Deleting model 'SimpleParticipant'
        db.delete_table(u'aktiviteter_simpleparticipant')


    models = {
        u'aktiviteter.aktivitet': {
            'Meta': {'object_name': 'Aktivitet'},
            'allow_simple_signup': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'association': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': u"orm['association.Association']"}),
            'audiences': ('django.db.models.fields.CharField', [], {'max_length': '1023'}),
            'category': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'category_tags': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'aktiviteter'", 'symmetrical': 'False', 'to': u"orm['core.Tag']"}),
            'co_association': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'null': 'True', 'to': u"orm['association.Association']"}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'difficulty': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'hidden': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'pub_date': ('django.db.models.fields.DateField', [], {}),
            'start_point': ('django.contrib.gis.db.models.fields.PointField', [], {'null': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'aktiviteter.aktivitetdate': {
            'Meta': {'object_name': 'AktivitetDate'},
            'aktivitet': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'dates'", 'to': u"orm['aktiviteter.Aktivitet']"}),
            'end_date': ('django.db.models.fields.DateTimeField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'participants': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'aktiviteter'", 'symmetrical': 'False', 'to': u"orm['user.User']"}),
            'signup_cancel_deadline': ('django.db.models.fields.DateField', [], {}),
            'signup_deadline': ('django.db.models.fields.DateField', [], {}),
            'signup_enabled': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'signup_start': ('django.db.models.fields.DateField', [], {}),
            'start_date': ('django.db.models.fields.DateTimeField', [], {}),
            'turledere': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'turleder_aktivitet_dates'", 'symmetrical': 'False', 'to': u"orm['user.User']"})
        },
        u'aktiviteter.aktivitetimage': {
            'Meta': {'object_name': 'AktivitetImage'},
            'aktivitet': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'images'", 'to': u"orm['aktiviteter.Aktivitet']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'order': ('django.db.models.fields.IntegerField', [], {}),
            'photographer': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'text': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '2048'})
        },
        u'aktiviteter.simpleparticipant': {
            'Meta': {'object_name': 'SimpleParticipant'},
            'aktivitet_date': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'simple_participants'", 'to': u"orm['aktiviteter.AktivitetDate']"}),
            'email': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'association.association': {
            'Meta': {'object_name': 'Association'},
            'counties': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'associations'", 'symmetrical': 'False', 'to': u"orm['core.County']"}),
            'email': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255'}),
            'facebook_url': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '2048'}),
            'focus_id': ('django.db.models.fields.IntegerField', [], {'default': 'None', 'null': 'True'}),
            'gmap_url': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '2048'}),
            'group_type': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'organization_no': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'children'", 'null': 'True', 'to': u"orm['association.Association']"}),
            'phone': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255'}),
            'post_address': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255'}),
            'site': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['core.Site']", 'unique': 'True', 'null': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'visit_address': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255'}),
            'zipcode': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.Zipcode']", 'null': 'True'})
        },
        u'core.county': {
            'Meta': {'object_name': 'County'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'core.site': {
            'Meta': {'object_name': 'Site'},
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'prefix': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'template': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.SiteTemplate']"})
        },
        u'core.sitetemplate': {
            'Meta': {'object_name': 'SiteTemplate'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'core.tag': {
            'Meta': {'object_name': 'Tag'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        u'core.zipcode': {
            'Meta': {'object_name': 'Zipcode'},
            'area': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'city_code': ('django.db.models.fields.CharField', [], {'max_length': '4'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'zipcode': ('django.db.models.fields.CharField', [], {'max_length': '4'})
        },
        u'user.associationrole': {
            'Meta': {'object_name': 'AssociationRole'},
            'association': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['association.Association']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'role': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['user.User']"})
        },
        u'user.permission': {
            'Meta': {'object_name': 'Permission'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'user.user': {
            'Meta': {'object_name': 'User'},
            'associations': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'+'", 'symmetrical': 'False', 'through': u"orm['user.AssociationRole']", 'to': u"orm['association.Association']"}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'identifier': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255', 'db_index': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'memberid': ('django.db.models.fields.IntegerField', [], {'unique': 'True', 'null': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'password_restore_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'password_restore_key': ('django.db.models.fields.CharField', [], {'max_length': '40', 'null': 'True'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'+'", 'symmetrical': 'False', 'to': u"orm['user.Permission']"}),
            'sherpa_email': ('django.db.models.fields.EmailField', [], {'max_length': '75'})
        }
    }

    complete_apps = ['aktiviteter']