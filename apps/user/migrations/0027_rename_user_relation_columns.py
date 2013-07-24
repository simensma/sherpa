# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models

class Migration(DataMigration):

    def forwards(self, orm):
        db.rename_column('admin_image', 'new_uploader_id', 'uploader_id')
        db.rename_table('aktiviteter_aktivitetdate_new_leaders', 'aktiviteter_aktivitetdate_leaders')
        db.rename_table('aktiviteter_aktivitetdate_new_participants', 'aktiviteter_aktivitetdate_participants')
        db.rename_column('articles_article', 'new_created_by_id', 'created_by_id')
        db.rename_column('articles_article', 'new_modified_by_id', 'modified_by_id')
        db.rename_column('page_page', 'new_created_by_id', 'created_by_id')
        db.rename_column('page_page', 'new_modified_by_id', 'modified_by_id')
        db.rename_column('page_variant', 'new_owner_id', 'owner_id')
        db.rename_column('page_version', 'new_owner_id', 'owner_id')
        db.rename_table('page_version_new_publishers', 'page_version_publishers')

    def backwards(self, orm):
        pass

    models = {
        u'admin.album': {
            'Meta': {'object_name': 'Album'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['admin.Album']", 'null': 'True'})
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
            'new_uploader': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['user.User']"}),
            'photographer': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'tags': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'images'", 'symmetrical': 'False', 'to': u"orm['core.Tag']"}),
            'uploaded': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'width': ('django.db.models.fields.IntegerField', [], {})
        },
        u'admin.imagerecovery': {
            'Meta': {'object_name': 'ImageRecovery'},
            'album': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['admin.Album']", 'null': 'True'}),
            'credits': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'exif': ('django.db.models.fields.TextField', [], {}),
            'extension': ('django.db.models.fields.CharField', [], {'max_length': '4'}),
            'hash': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'height': ('django.db.models.fields.IntegerField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '8'}),
            'licence': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'photographer': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'tags': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'+'", 'symmetrical': 'False', 'to': u"orm['core.Tag']"}),
            'uploaded': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'width': ('django.db.models.fields.IntegerField', [], {})
        },
        u'admin.publication': {
            'Meta': {'object_name': 'Publication'},
            'access': ('django.db.models.fields.CharField', [], {'default': "'all'", 'max_length': '255'}),
            'association': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['association.Association']"}),
            'description': ('django.db.models.fields.TextField', [], {}),
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
            'new_leaders': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'new_leader_aktivitet_dates'", 'symmetrical': 'False', 'to': u"orm['user.User']"}),
            'new_participants': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'new_aktiviteter'", 'symmetrical': 'False', 'to': u"orm['user.User']"}),
            'signup_cancel_deadline': ('django.db.models.fields.DateField', [], {}),
            'signup_deadline': ('django.db.models.fields.DateField', [], {}),
            'signup_enabled': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'signup_start': ('django.db.models.fields.DateField', [], {}),
            'start_date': ('django.db.models.fields.DateTimeField', [], {})
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
        u'analytics.segment': {
            'Meta': {'object_name': 'Segment'},
            'description': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        u'articles.article': {
            'Meta': {'object_name': 'Article'},
            'created_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'hide_thumbnail': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'new_created_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'new_articles_created'", 'to': u"orm['user.User']"}),
            'new_modified_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'new_articles_modified'", 'null': 'True', 'to': u"orm['user.User']"}),
            'pub_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'published': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.Site']"}),
            'thumbnail': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True'})
        },
        u'articles.oldarticle': {
            'Meta': {'object_name': 'OldArticle'},
            'author_email': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'author_name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'content': ('django.db.models.fields.TextField', [], {}),
            'date': ('django.db.models.fields.DateTimeField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lede': ('django.db.models.fields.TextField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
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
        u'fjelltreffen.annonse': {
            'Meta': {'object_name': 'Annonse'},
            'county': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.County']", 'null': 'True'}),
            'date_added': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_renewed': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'hidden': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'hideage': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.CharField', [], {'max_length': '2048'}),
            'image_thumb': ('django.db.models.fields.CharField', [], {'max_length': '2048'}),
            'is_image_old': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'text': ('django.db.models.fields.TextField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'new_fjelltreffen_annonser'", 'to': u"orm['user.User']"})
        },
        u'membership.smsservicerequest': {
            'Meta': {'object_name': 'SMSServiceRequest'},
            'blocked': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'count': ('django.db.models.fields.IntegerField', [], {}),
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip': ('django.db.models.fields.CharField', [], {'max_length': '15'}),
            'memberid': ('django.db.models.fields.IntegerField', [], {'max_length': '255', 'null': 'True'}),
            'phone_number_input': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['user.User']", 'null': 'True'})
        },
        u'page.ad': {
            'Meta': {'object_name': 'Ad'},
            'content_type': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'destination': ('django.db.models.fields.CharField', [], {'max_length': '2048'}),
            'extension': ('django.db.models.fields.CharField', [], {'max_length': '4'}),
            'fallback_content_type': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True'}),
            'fallback_extension': ('django.db.models.fields.CharField', [], {'max_length': '4', 'null': 'True'}),
            'fallback_sha1_hash': ('django.db.models.fields.CharField', [], {'max_length': '40', 'null': 'True'}),
            'height': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'sha1_hash': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'viewcounter': ('django.db.models.fields.CharField', [], {'max_length': '2048'}),
            'width': ('django.db.models.fields.IntegerField', [], {'null': 'True'})
        },
        u'page.adplacement': {
            'Meta': {'object_name': 'AdPlacement'},
            'ad': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['page.Ad']"}),
            'clicks': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'end_date': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'start_date': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'view_limit': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'views': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        u'page.column': {
            'Meta': {'object_name': 'Column'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'offset': ('django.db.models.fields.IntegerField', [], {}),
            'order': ('django.db.models.fields.IntegerField', [], {}),
            'row': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['page.Row']"}),
            'span': ('django.db.models.fields.IntegerField', [], {})
        },
        u'page.content': {
            'Meta': {'object_name': 'Content'},
            'column': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['page.Column']"}),
            'content': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'order': ('django.db.models.fields.IntegerField', [], {}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'page.menu': {
            'Meta': {'object_name': 'Menu'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'order': ('django.db.models.fields.IntegerField', [], {}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.Site']"}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '2048'})
        },
        u'page.page': {
            'Meta': {'object_name': 'Page'},
            'created_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'new_created_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'new_pages_created'", 'to': u"orm['user.User']"}),
            'new_modified_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'new_pages_modified'", 'null': 'True', 'to': u"orm['user.User']"}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['page.Page']", 'null': 'True'}),
            'pub_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'published': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.Site']"}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'page.row': {
            'Meta': {'object_name': 'Row'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'order': ('django.db.models.fields.IntegerField', [], {}),
            'version': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['page.Version']"})
        },
        u'page.variant': {
            'Meta': {'object_name': 'Variant'},
            'article': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['articles.Article']", 'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'new_owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': u"orm['user.User']"}),
            'page': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['page.Page']", 'null': 'True'}),
            'priority': ('django.db.models.fields.IntegerField', [], {}),
            'segment': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['analytics.Segment']", 'null': 'True'})
        },
        u'page.version': {
            'Meta': {'object_name': 'Version'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'ads': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'new_owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': u"orm['user.User']"}),
            'new_publishers': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'new_versions'", 'symmetrical': 'False', 'to': u"orm['user.User']"}),
            'tags': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'versions'", 'symmetrical': 'False', 'to': u"orm['core.Tag']"}),
            'variant': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['page.Variant']"}),
            'version': ('django.db.models.fields.IntegerField', [], {})
        },
        u'user.associationrole': {
            'Meta': {'object_name': 'AssociationRole'},
            'association': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['association.Association']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'role': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['user.User']"})
        },
        u'user.norwaybusticket': {
            'Meta': {'object_name': 'NorwayBusTicket'},
            'date_placed': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_trip': ('django.db.models.fields.DateTimeField', [], {}),
            'distance': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'new_norway_bus_ticket'", 'unique': 'True', 'to': u"orm['user.User']"})
        },
        u'user.norwaybusticketold': {
            'Meta': {'object_name': 'NorwayBusTicketOld'},
            'date_placed': ('django.db.models.fields.DateTimeField', [], {}),
            'date_trip_text': ('django.db.models.fields.CharField', [], {'max_length': '25'}),
            'distance': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'memberid': ('django.db.models.fields.IntegerField', [], {'unique': 'True'})
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
            'sherpa_email': ('django.db.models.fields.EmailField', [], {'max_length': '75'})
        }
    }

    complete_apps = ['admin', 'aktiviteter', 'articles', 'fjelltreffen', 'membership', 'page', 'user']
    symmetrical = True
