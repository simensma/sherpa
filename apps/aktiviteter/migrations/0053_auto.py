# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding M2M table for field cabins on 'ConversionFailure'
        db.create_table(u'aktiviteter_conversionfailure_cabins', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('conversionfailure', models.ForeignKey(orm[u'aktiviteter.conversionfailure'], null=False)),
            ('cabin', models.ForeignKey(orm[u'aktiviteter.cabin'], null=False))
        ))
        db.create_unique(u'aktiviteter_conversionfailure_cabins', ['conversionfailure_id', 'cabin_id'])


    def backwards(self, orm):
        # Removing M2M table for field cabins on 'ConversionFailure'
        db.delete_table('aktiviteter_conversionfailure_cabins')


    models = {
        u'aktiviteter.aktivitet': {
            'Meta': {'object_name': 'Aktivitet'},
            'audiences': ('django.db.models.fields.CharField', [], {'max_length': '1023'}),
            'category': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'category_tags': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'aktiviteter'", 'symmetrical': 'False', 'to': u"orm['core.Tag']"}),
            'category_type': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True'}),
            'co_foreninger': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'aktiviteter'", 'null': 'True', 'to': u"orm['foreninger.Forening']"}),
            'co_foreninger_cabin': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'+'", 'null': 'True', 'to': u"orm['aktiviteter.Cabin']"}),
            'code': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'counties': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'aktiviteter'", 'symmetrical': 'False', 'to': u"orm['core.County']"}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'difficulty': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'forening': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'null': 'True', 'to': u"orm['foreninger.Forening']"}),
            'forening_cabin': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'null': 'True', 'to': u"orm['aktiviteter.Cabin']"}),
            'getting_there': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'locations': ('django.db.models.fields.CharField', [], {'max_length': '4091'}),
            'municipalities': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'aktiviteter'", 'symmetrical': 'False', 'to': u"orm['core.Municipality']"}),
            'private': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'pub_date': ('django.db.models.fields.DateField', [], {}),
            'published': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'sherpa2_id': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'start_point': ('django.contrib.gis.db.models.fields.PointField', [], {'null': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'turforslag': ('django.db.models.fields.IntegerField', [], {'null': 'True'})
        },
        u'aktiviteter.aktivitetdate': {
            'Meta': {'object_name': 'AktivitetDate'},
            'aktivitet': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'dates'", 'to': u"orm['aktiviteter.Aktivitet']"}),
            'contact_custom_email': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'contact_custom_name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'contact_custom_phone': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'contact_type': ('django.db.models.fields.CharField', [], {'default': "u'arrang\\xf8r'", 'max_length': '255'}),
            'end_date': ('django.db.models.fields.DateTimeField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'meeting_place': ('django.db.models.fields.TextField', [], {}),
            'meeting_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'participants': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'aktiviteter'", 'symmetrical': 'False', 'to': u"orm['user.User']"}),
            'should_have_turleder': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'signup_cancel_deadline': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'signup_deadline': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'signup_enabled': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'signup_max_allowed': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0', 'null': 'True'}),
            'signup_simple_allowed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'signup_start': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'start_date': ('django.db.models.fields.DateTimeField', [], {}),
            'turledere': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'turleder_aktivitet_dates'", 'symmetrical': 'False', 'to': u"orm['user.User']"})
        },
        u'aktiviteter.aktivitetimage': {
            'Meta': {'object_name': 'AktivitetImage'},
            'aktivitet': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'images'", 'to': u"orm['aktiviteter.Aktivitet']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'order': ('django.db.models.fields.IntegerField', [], {}),
            'photographer': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'sherpa2_url': ('django.db.models.fields.CharField', [], {'max_length': '1023', 'null': 'True'}),
            'text': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '2048'})
        },
        u'aktiviteter.cabin': {
            'Meta': {'object_name': 'Cabin'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'sherpa2_id': ('django.db.models.fields.PositiveIntegerField', [], {})
        },
        u'aktiviteter.conversionfailure': {
            'Meta': {'object_name': 'ConversionFailure'},
            'cabins': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'failed_imports'", 'null': 'True', 'to': u"orm['aktiviteter.Cabin']"}),
            'foreninger': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'failed_imports'", 'null': 'True', 'to': u"orm['foreninger.Forening']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'reason': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'sherpa2_id': ('django.db.models.fields.PositiveIntegerField', [], {})
        },
        u'aktiviteter.simpleparticipant': {
            'Meta': {'object_name': 'SimpleParticipant'},
            'aktivitet_date': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'simple_participants'", 'to': u"orm['aktiviteter.AktivitetDate']"}),
            'email': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'core.county': {
            'Meta': {'object_name': 'County'},
            'area': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'code': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'geom': ('django.contrib.gis.db.models.fields.MultiPolygonField', [], {'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'perimeter': ('django.db.models.fields.FloatField', [], {'null': 'True'})
        },
        u'core.municipality': {
            'Meta': {'object_name': 'Municipality'},
            'area': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'code': ('django.db.models.fields.CharField', [], {'max_length': '4'}),
            'geom': ('django.contrib.gis.db.models.fields.MultiPolygonField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'perimeter': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'update_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True'})
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
        u'foreninger.forening': {
            'Meta': {'ordering': "['name']", 'object_name': 'Forening'},
            'contact_person': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['user.User']", 'null': 'True'}),
            'contact_person_name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255'}),
            'counties': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'foreninger'", 'symmetrical': 'False', 'to': u"orm['core.County']"}),
            'email': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255'}),
            'facebook_url': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '2048'}),
            'focus_id': ('django.db.models.fields.IntegerField', [], {'default': 'None', 'null': 'True'}),
            'gmap_url': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '2048'}),
            'group_type': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'organization_no': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255'}),
            'parents': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'children'", 'symmetrical': 'False', 'to': u"orm['foreninger.Forening']"}),
            'phone': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255'}),
            'post_address': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'visit_address': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255'}),
            'zipcode': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.Zipcode']", 'null': 'True'})
        },
        u'user.foreningrole': {
            'Meta': {'object_name': 'ForeningRole'},
            'forening': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['foreninger.Forening']"}),
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
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'foreninger': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'+'", 'symmetrical': 'False', 'through': u"orm['user.ForeningRole']", 'to': u"orm['foreninger.Forening']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'identifier': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255', 'db_index': 'True'}),
            'is_expired': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_inactive': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_pending': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'memberid': ('django.db.models.fields.IntegerField', [], {'unique': 'True', 'null': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'password_restore_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'password_restore_key': ('django.db.models.fields.CharField', [], {'max_length': '40', 'null': 'True'}),
            'pending_registration_key': ('django.db.models.fields.CharField', [], {'max_length': '40', 'null': 'True'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'+'", 'symmetrical': 'False', 'to': u"orm['user.Permission']"}),
            'sherpa_email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'turleder_active_foreninger': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'active_turledere'", 'symmetrical': 'False', 'to': u"orm['foreninger.Forening']"})
        }
    }

    complete_apps = ['aktiviteter']