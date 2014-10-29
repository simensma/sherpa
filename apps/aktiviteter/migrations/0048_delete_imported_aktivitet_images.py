# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models
from django.conf import settings
from core.util import s3_bucket
import boto

class Migration(DataMigration):

    def forwards(self, orm):
        # Delete references from all imported aktiviteter
        for aktivitet in orm['aktiviteter.Aktivitet'].objects.filter(sherpa2_id__isnull=False):
            aktivitet.images.all().delete()

        # Delete all images in the album - note that post-delete hooks don't work here, so we'll delete the images
        # from S3 explicitly
        for image in orm['admin.Image'].objects.filter(album=66):
            conn = boto.connect_s3(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)
            bucket = conn.get_bucket(s3_bucket())
            bucket.delete_key("%s%s.%s" % (
                settings.AWS_IMAGEGALLERY_PREFIX,
                image.key,
                image.extension
            ))
            for size in settings.THUMB_SIZES:
                bucket.delete_key("%s%s-%s.%s" % (
                    settings.AWS_IMAGEGALLERY_PREFIX,
                    image.key,
                    str(size),
                    image.extension
                ))
            image.delete()

    def backwards(self, orm):
        "Write your backwards methods here."

    models = {
        u'admin.album': {
            'Meta': {'object_name': 'Album'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['admin.Album']", 'null': 'True'})
        },
        u'admin.campaign': {
            'Meta': {'ordering': "['-created']", 'object_name': 'Campaign'},
            'button_anchor': ('django.db.models.fields.CharField', [], {'max_length': '2048'}),
            'button_enabled': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'button_label': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
            'button_large': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'button_position': ('django.db.models.fields.CharField', [], {'max_length': '512'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'ga_event_label': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image_crop': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
            'image_cropped_hash': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'image_original': ('django.db.models.fields.CharField', [], {'max_length': '2048'}),
            'photographer': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'photographer_alignment': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'photographer_color': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.Site']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'utm_campaign': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'admin.campaigntext': {
            'Meta': {'ordering': "['id']", 'object_name': 'CampaignText'},
            'campaign': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'text'", 'to': u"orm['admin.Campaign']"}),
            'content': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'style': ('django.db.models.fields.CharField', [], {'max_length': '1024'})
        },
        u'admin.fotokonkurranse': {
            'Meta': {'object_name': 'Fotokonkurranse'},
            'album': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['admin.Album']", 'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'admin.image': {
            'Meta': {'object_name': 'Image'},
            'album': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['admin.Album']", 'null': 'True'}),
            'credits': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'exif': ('django.db.models.fields.TextField', [], {}),
            'extension': ('django.db.models.fields.CharField', [], {'max_length': '4'}),
            'hash': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'height': ('django.db.models.fields.IntegerField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '8'}),
            'licence': ('django.db.models.fields.CharField', [], {'max_length': '1023'}),
            'photographer': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'tags': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'images'", 'symmetrical': 'False', 'to': u"orm['core.Tag']"}),
            'uploaded': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'uploader': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['user.User']", 'null': 'True'}),
            'width': ('django.db.models.fields.IntegerField', [], {})
        },
        u'admin.publication': {
            'Meta': {'object_name': 'Publication'},
            'access': ('django.db.models.fields.CharField', [], {'default': "'all'", 'max_length': '255'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'forening': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['foreninger.Forening']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'license': ('django.db.models.fields.CharField', [], {'default': "'all_rights_reserved'", 'max_length': '255'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'admin.release': {
            'Meta': {'object_name': 'Release'},
            'cover_photo': ('django.db.models.fields.CharField', [], {'max_length': '2048'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'online_view': ('django.db.models.fields.CharField', [], {'max_length': '2048'}),
            'pdf_file_size': ('django.db.models.fields.IntegerField', [], {'default': 'None', 'null': 'True'}),
            'pdf_hash': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'pub_date': ('django.db.models.fields.DateTimeField', [], {}),
            'publication': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'releases'", 'to': u"orm['admin.Publication']"}),
            'tags': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'releases'", 'symmetrical': 'False', 'to': u"orm['core.Tag']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
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
        u'aktiviteter.importfailure': {
            'Meta': {'object_name': 'ImportFailure'},
            'forening': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'null': 'True', 'to': u"orm['foreninger.Forening']"}),
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
        u'core.site': {
            'Meta': {'object_name': 'Site'},
            'analytics_ua': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True'}),
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'forening': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'sites'", 'to': u"orm['foreninger.Forening']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_published': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'prefix': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'template': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '255'})
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

    complete_apps = ['admin', 'aktiviteter']
    symmetrical = True
