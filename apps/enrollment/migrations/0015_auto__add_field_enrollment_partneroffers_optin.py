# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Enrollment.partneroffers_optin'
        db.add_column(u'enrollment_enrollment', 'partneroffers_optin',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Enrollment.partneroffers_optin'
        db.delete_column(u'enrollment_enrollment', 'partneroffers_optin')


    models = {
        u'core.county': {
            'Meta': {'object_name': 'County'},
            'area': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'code': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'geom': ('django.contrib.gis.db.models.fields.MultiPolygonField', [], {'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'perimeter': ('django.db.models.fields.FloatField', [], {'null': 'True'})
        },
        u'core.zipcode': {
            'Meta': {'object_name': 'Zipcode'},
            'area': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'city_code': ('django.db.models.fields.CharField', [], {'max_length': '4'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'zipcode': ('django.db.models.fields.CharField', [], {'max_length': '4'})
        },
        u'enrollment.enrollment': {
            'Meta': {'object_name': 'Enrollment'},
            'accepts_conditions': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'address1': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'address2': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'address3': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'area': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'attempted_yearbook': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'country': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'date_initiated': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'existing_memberid': ('django.db.models.fields.CharField', [], {'max_length': '51'}),
            'forening': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'null': 'True', 'to': u"orm['foreninger.Forening']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'partneroffers_optin': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'payment_method': ('django.db.models.fields.CharField', [], {'max_length': '51'}),
            'result': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'wants_yearbook': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'zipcode': ('django.db.models.fields.CharField', [], {'max_length': '51'})
        },
        u'enrollment.state': {
            'Meta': {'object_name': 'State'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'card': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'enrollment.transaction': {
            'Meta': {'ordering': "['-initiated']", 'object_name': 'Transaction'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'enrollment': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'transactions'", 'to': u"orm['enrollment.Enrollment']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'initiated': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'order_number': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'state': ('django.db.models.fields.CharField', [], {'default': "'register'", 'max_length': '255'}),
            'transaction_id': ('django.db.models.fields.CharField', [], {'max_length': '32'})
        },
        u'enrollment.user': {
            'Meta': {'object_name': 'User'},
            'chosen_main_member': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'dob': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'email': ('django.db.models.fields.CharField', [], {'max_length': '511'}),
            'enrollment': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'users'", 'to': u"orm['enrollment.Enrollment']"}),
            'gender': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'memberid': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '511'}),
            'pending_user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'null': 'True', 'to': u"orm['user.User']"}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'sms_sent': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
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

    complete_apps = ['enrollment']