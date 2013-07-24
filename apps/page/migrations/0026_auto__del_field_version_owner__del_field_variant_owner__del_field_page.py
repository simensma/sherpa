# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'Version.owner'
        db.delete_column(u'page_version', 'owner_id')

        # Removing M2M table for field publishers on 'Version'
        db.delete_table('page_version_publishers')

        # Deleting field 'Variant.owner'
        db.delete_column(u'page_variant', 'owner_id')

        # Deleting field 'Page.modified_by'
        db.delete_column(u'page_page', 'modified_by_id')

        # Deleting field 'Page.created_by'
        db.delete_column(u'page_page', 'created_by_id')


    def backwards(self, orm):

        # User chose to not deal with backwards NULL issues for 'Version.owner'
        raise RuntimeError("Cannot reverse this migration. 'Version.owner' and its values cannot be restored.")
        # Adding M2M table for field publishers on 'Version'
        db.create_table(u'page_version_publishers', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('version', models.ForeignKey(orm[u'page.version'], null=False)),
            ('profile', models.ForeignKey(orm[u'user.profile'], null=False))
        ))
        db.create_unique(u'page_version_publishers', ['version_id', 'profile_id'])


        # User chose to not deal with backwards NULL issues for 'Variant.owner'
        raise RuntimeError("Cannot reverse this migration. 'Variant.owner' and its values cannot be restored.")
        # Adding field 'Page.modified_by'
        db.add_column(u'page_page', 'modified_by',
                      self.gf('django.db.models.fields.related.ForeignKey')(related_name='pages_modified', null=True, to=orm['user.Profile']),
                      keep_default=False)


        # User chose to not deal with backwards NULL issues for 'Page.created_by'
        raise RuntimeError("Cannot reverse this migration. 'Page.created_by' and its values cannot be restored.")

    models = {
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

    complete_apps = ['page']