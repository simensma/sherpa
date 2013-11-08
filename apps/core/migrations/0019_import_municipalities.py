# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models

class Migration(DataMigration):

    def forwards(self, orm):
        # Exclude apparent duplicates based on which dupe has correct geometries
        for k in orm['sherpa2.Kommuner'].objects.exclude(pk__in=[66, 109, 78, 230]):
            m = orm['core.Municipality']()
            if k.komm < 1000:
                m.code = '0%s' % k.komm
            else:
                m.code = '%s' % k.komm

            # Rewrite format for names including Sami
            if k.pk == 252:
                m.name = 'Kåfjord (Gáivuotna)'
            elif k.pk == 287:
                m.name = 'Kautokeino (Guovdageaidnu)'
            elif k.pk == 286:
                m.name = 'Karasjok (Kárásjohka)'
            elif k.pk == 284:
                m.name = 'Porsanger (Porsàngu, Porsanki)'
            elif k.pk == 251:
                m.name = 'Nesseby (Unjárga)'
            elif k.pk == 44:
                m.name = 'Tana (Deatnu)'
            else:
                m.name = k.navn

            m.area = k.area
            m.perimeter = k.perimeter
            m.geom = k.the_geom

            if k.oppdatdato is None:
                m.update_date = None
            else:
                m.update_date = datetime.datetime.strptime(k.oppdatdato, "%d.%m.%Y")

            m.save()

    def backwards(self, orm):
        "Write your backwards methods here."

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
        u'core.focuscountry': {
            'Meta': {'object_name': 'FocusCountry'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'scandinavian': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
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
        u'core.zipcodestate': {
            'Meta': {'object_name': 'ZipcodeState'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_update': ('django.db.models.fields.DateTimeField', [], {})
        },
        u'sherpa2.article': {
            'Meta': {'object_name': 'Article', 'db_table': "u'article'"},
            'author': ('django.db.models.fields.CharField', [], {'max_length': '100', 'db_column': "'ar_author'", 'blank': 'True'}),
            'author_email': ('django.db.models.fields.CharField', [], {'max_length': '100', 'db_column': "'ar_author_email'", 'blank': 'True'}),
            'content': ('django.db.models.fields.TextField', [], {'db_column': "'ar_content'", 'blank': 'True'}),
            'date': ('django.db.models.fields.CharField', [], {'max_length': '12', 'db_column': "'ar_date'", 'blank': 'True'}),
            'date_in': ('django.db.models.fields.CharField', [], {'max_length': '12', 'db_column': "'ar_date_in'", 'blank': 'True'}),
            'date_out': ('django.db.models.fields.CharField', [], {'max_length': '12', 'db_column': "'ar_date_out'", 'blank': 'True'}),
            'folders': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'articles'", 'symmetrical': 'False', 'through': u"orm['sherpa2.FolderArticle']", 'to': u"orm['sherpa2.Folder']"}),
            'id': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True', 'db_column': "'ar_id'"}),
            'lede': ('django.db.models.fields.TextField', [], {'db_column': "'ar_ingress'", 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'db_column': "'ar_name'", 'blank': 'True'}),
            'online': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'db_column': "'ar_online'", 'blank': 'True'}),
            'orig_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'db_column': "'ar_orig_id'", 'blank': 'True'}),
            'owner': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'db_column': "'ar_owner'", 'blank': 'True'}),
            'priority': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'db_column': "'ar_priority'", 'blank': 'True'}),
            'rel_cabins': ('django.db.models.fields.TextField', [], {'db_column': "'ar_rel_cabins'", 'blank': 'True'}),
            'rel_locations': ('django.db.models.fields.TextField', [], {'db_column': "'ar_rel_locations'", 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '20', 'db_column': "'ar_status'", 'blank': 'True'})
        },
        u'sherpa2.association': {
            'Meta': {'object_name': 'Association', 'db_table': "u'groups'"},
            'account': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_column': "'gr_account'", 'blank': 'True'}),
            'content': ('django.db.models.fields.TextField', [], {'db_column': "'gr_content'", 'blank': 'True'}),
            'country': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_column': "'gr_country'", 'blank': 'True'}),
            'county': ('django.db.models.fields.TextField', [], {'db_column': "'gr_county'", 'blank': 'True'}),
            'date': ('django.db.models.fields.CharField', [], {'max_length': '12', 'db_column': "'gr_date'", 'blank': 'True'}),
            'email': ('django.db.models.fields.CharField', [], {'max_length': '100', 'db_column': "'gr_email'", 'blank': 'True'}),
            'employees': ('django.db.models.fields.DecimalField', [], {'blank': 'True', 'null': 'True', 'db_column': "'gr_employees'", 'decimal_places': '2', 'max_digits': '5'}),
            'facebook': ('django.db.models.fields.TextField', [], {'db_column': "'gr_facebook'", 'blank': 'True'}),
            'fax': ('django.db.models.fields.CharField', [], {'max_length': '30', 'db_column': "'gr_fax'", 'blank': 'True'}),
            'fo_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'db_column': "'gr_fo_id'", 'blank': 'True'}),
            'focus_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'db_column': "'gr_my_id'", 'blank': 'True'}),
            'id': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True', 'db_column': "'gr_id'"}),
            'lang': ('django.db.models.fields.CharField', [], {'max_length': '3', 'db_column': "'gr_lang'", 'blank': 'True'}),
            'legal_url': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_column': "'gr_legal_url'", 'blank': 'True'}),
            'map': ('django.db.models.fields.TextField', [], {'db_column': "'gr_map'", 'blank': 'True'}),
            'member_email': ('django.db.models.fields.CharField', [], {'max_length': '100', 'db_column': "'gr_member_email'", 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'db_column': "'gr_name'", 'blank': 'True'}),
            'online': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'db_column': "'gr_online'", 'blank': 'True'}),
            'orgnr': ('django.db.models.fields.CharField', [], {'max_length': '20', 'db_column': "'gr_orgnr'", 'blank': 'True'}),
            'parent': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'db_column': "'gr_parent'", 'blank': 'True'}),
            'path': ('django.db.models.fields.CharField', [], {'max_length': '100', 'db_column': "'gr_path'", 'blank': 'True'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '30', 'db_column': "'gr_phone'", 'blank': 'True'}),
            'post_address': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_column': "'gr_adress1'", 'blank': 'True'}),
            'risk_url': ('django.db.models.fields.TextField', [], {'db_column': "'gr_risk_url'", 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '20', 'db_column': "'gr_status'", 'blank': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_column': "'gr_type'", 'blank': 'True'}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_column': "'gr_url'", 'blank': 'True'}),
            'visible': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'db_column': "'gr_visible'", 'blank': 'True'}),
            'visit_address': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_column': "'gr_adress2'", 'blank': 'True'}),
            'ziparea': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_column': "'gr_ziparea'", 'blank': 'True'}),
            'zipcode': ('django.db.models.fields.CharField', [], {'max_length': '12', 'db_column': "'gr_zip'", 'blank': 'True'})
        },
        u'sherpa2.cabin': {
            'Meta': {'object_name': 'Cabin', 'db_table': "u'cabin2'"},
            'access': ('django.db.models.fields.TextField', [], {'db_column': "u'ca_access'", 'blank': 'True'}),
            'access_summer': ('django.db.models.fields.TextField', [], {'db_column': "u'ca_access_summer'", 'blank': 'True'}),
            'access_winter': ('django.db.models.fields.TextField', [], {'db_column': "u'ca_access_winter'", 'blank': 'True'}),
            'address_in_season': ('django.db.models.fields.TextField', [], {'db_column': "u'ca_address_in_season'", 'blank': 'True'}),
            'address_out_of_season': ('django.db.models.fields.TextField', [], {'db_column': "u'ca_address_out_of_season'", 'blank': 'True'}),
            'album': ('django.db.models.fields.TextField', [], {'db_column': "u'ca_album'", 'blank': 'True'}),
            'alias': ('django.db.models.fields.TextField', [], {'db_column': "u'ca_alias'", 'blank': 'True'}),
            'altitude': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'db_column': "u'ca_altitude'", 'blank': 'True'}),
            'beds_b': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'db_column': "u'ca_beds_b'", 'blank': 'True'}),
            'beds_extras': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'db_column': "u'ca_beds_extras'", 'blank': 'True'}),
            'beds_s': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'db_column': "u'ca_beds_s'", 'blank': 'True'}),
            'beds_u': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'db_column': "u'ca_beds_u'", 'blank': 'True'}),
            'beds_winter': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'db_column': "u'ca_beds_winter'", 'blank': 'True'}),
            'booking_url': ('django.db.models.fields.TextField', [], {'db_column': "u'ca_booking_url'", 'blank': 'True'}),
            'built': ('django.db.models.fields.TextField', [], {'db_column': "u'ca_built'", 'blank': 'True'}),
            'contact_in_season': ('django.db.models.fields.TextField', [], {'db_column': "u'ca_contact_in_season'", 'blank': 'True'}),
            'contact_out_of_season': ('django.db.models.fields.TextField', [], {'db_column': "u'ca_contact_out_of_season'", 'blank': 'True'}),
            'content': ('django.db.models.fields.TextField', [], {'db_column': "u'ca_content'", 'blank': 'True'}),
            'content_eng': ('django.db.models.fields.TextField', [], {'db_column': "u'ca_content_eng'", 'blank': 'True'}),
            'content_extended': ('django.db.models.fields.TextField', [], {'db_column': "u'ca_content_extended'", 'blank': 'True'}),
            'content_fre': ('django.db.models.fields.TextField', [], {'db_column': "u'ca_content_fre'", 'blank': 'True'}),
            'content_ger': ('django.db.models.fields.TextField', [], {'db_column': "u'ca_content_ger'", 'blank': 'True'}),
            'content_nno': ('django.db.models.fields.TextField', [], {'db_column': "u'ca_content_nno'", 'blank': 'True'}),
            'county': ('django.db.models.fields.TextField', [], {'db_column': "u'ca_county'", 'blank': 'True'}),
            'email_in_season': ('django.db.models.fields.TextField', [], {'db_column': "u'ca_email_in_season'", 'blank': 'True'}),
            'email_out_of_season': ('django.db.models.fields.TextField', [], {'db_column': "u'ca_email_out_of_season'", 'blank': 'True'}),
            'extras': ('django.db.models.fields.TextField', [], {'db_column': "u'ca_extras'", 'blank': 'True'}),
            'fax_in_season': ('django.db.models.fields.TextField', [], {'db_column': "u'ca_fax_in_season'", 'blank': 'True'}),
            'fax_out_of_season': ('django.db.models.fields.TextField', [], {'db_column': "u'ca_fax_out_of_season'", 'blank': 'True'}),
            'id': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True', 'db_column': "u'ca_id'"}),
            'lat': ('django.db.models.fields.DecimalField', [], {'blank': 'True', 'null': 'True', 'db_column': "u'ca_lat'", 'decimal_places': '65535', 'max_digits': '65535'}),
            'location': ('django.db.models.fields.TextField', [], {'db_column': "u'ca_location'", 'blank': 'True'}),
            'lon': ('django.db.models.fields.DecimalField', [], {'blank': 'True', 'null': 'True', 'db_column': "u'ca_lon'", 'decimal_places': '65535', 'max_digits': '65535'}),
            'm711': ('django.db.models.fields.TextField', [], {'db_column': "u'ca_m711'", 'blank': 'True'}),
            'm711_nb': ('django.db.models.fields.TextField', [], {'db_column': "u'ca_m711_nb'", 'blank': 'True'}),
            'maintainer': ('django.db.models.fields.IntegerField', [], {'db_column': "u'ca_maintainer'"}),
            'map': ('django.db.models.fields.TextField', [], {'db_column': "u'ca_map'", 'blank': 'True'}),
            'map_nb': ('django.db.models.fields.TextField', [], {'db_column': "u'ca_map_nb'", 'blank': 'True'}),
            'mobile_in_season': ('django.db.models.fields.TextField', [], {'db_column': "u'ca_mobile_in_season'", 'blank': 'True'}),
            'mobile_out_of_season': ('django.db.models.fields.TextField', [], {'db_column': "u'ca_mobile_out_of_season'", 'blank': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'db_column': "u'ca_modified'", 'blank': 'True'}),
            'modified_by': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'db_column': "u'ca_modified_by'", 'blank': 'True'}),
            'municipality': ('django.db.models.fields.TextField', [], {'db_column': "u'ca_municipality'", 'blank': 'True'}),
            'municipality_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'db_column': "u'ca_municipality_id'", 'blank': 'True'}),
            'name': ('django.db.models.fields.TextField', [], {'db_column': "u'ca_name'"}),
            'name_official': ('django.db.models.fields.TextField', [], {'db_column': "u'ca_name_official'", 'blank': 'True'}),
            'nr': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'db_column': "u'ca_nr'", 'blank': 'True'}),
            'online': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'db_column': "u'ca_online'", 'blank': 'True'}),
            'owner': ('django.db.models.fields.IntegerField', [], {'db_column': "u'ca_owner'"}),
            'phone_in_season': ('django.db.models.fields.TextField', [], {'db_column': "u'ca_phone_in_season'", 'blank': 'True'}),
            'phone_out_of_season': ('django.db.models.fields.TextField', [], {'db_column': "u'ca_phone_out_of_season'", 'blank': 'True'}),
            'price': ('django.db.models.fields.TextField', [], {'db_column': "u'ca_price'", 'blank': 'True'}),
            'service': ('django.db.models.fields.TextField', [], {'db_column': "u'ca_service'", 'blank': 'True'}),
            'source': ('django.db.models.fields.TextField', [], {'db_column': "u'ca_source'", 'blank': 'True'}),
            'ssr_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'db_column': "u'ca_ssr_id'", 'blank': 'True'}),
            'ssr_obj_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'db_column': "u'ca_ssr_obj_id'", 'blank': 'True'}),
            'ssr_type': ('django.db.models.fields.TextField', [], {'db_column': "u'ca_ssr_type'", 'blank': 'True'}),
            'ssr_type_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'db_column': "u'ca_ssr_type_id'", 'blank': 'True'}),
            'startdate': ('django.db.models.fields.TextField', [], {'db_column': "u'ca_startdate'", 'blank': 'True'}),
            'status': ('django.db.models.fields.TextField', [], {'db_column': "u'ca_status'", 'blank': 'True'}),
            'the_geom': ('django.contrib.gis.db.models.fields.GeometryField', [], {'blank': 'True'}),
            'type': ('django.db.models.fields.TextField', [], {'db_column': "u'ca_type'", 'blank': 'True'}),
            'url': ('django.db.models.fields.TextField', [], {'db_column': "u'ca_url'", 'blank': 'True'}),
            'url_ut': ('django.db.models.fields.TextField', [], {'db_column': "u'ca_url_ut'", 'blank': 'True'}),
            'utm': ('django.db.models.fields.TextField', [], {'db_column': "u'ca_utm'", 'blank': 'True'}),
            'utm_gps': ('django.db.models.fields.TextField', [], {'db_column': "u'ca_utm_gps'", 'blank': 'True'}),
            'yr_url': ('django.db.models.fields.TextField', [], {'db_column': "u'ca_yr_url'", 'blank': 'True'})
        },
        u'sherpa2.condition': {
            'Meta': {'object_name': 'Condition', 'db_table': "u'conditions'"},
            'author_email': ('django.db.models.fields.CharField', [], {'max_length': '200', 'db_column': "'co_author_email'", 'blank': 'True'}),
            'author_name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'db_column': "'co_author_name'", 'blank': 'True'}),
            'content': ('django.db.models.fields.TextField', [], {'db_column': "'co_content'", 'blank': 'True'}),
            'date_changed': ('django.db.models.fields.CharField', [], {'max_length': '14', 'db_column': "'co_date_changed'"}),
            'date_created': ('django.db.models.fields.CharField', [], {'max_length': '14', 'db_column': "'co_date_created'"}),
            'date_observed': ('django.db.models.fields.CharField', [], {'max_length': '8', 'db_column': "'co_date_observed'"}),
            'deleted': ('django.db.models.fields.IntegerField', [], {'db_column': "'co_deleted'"}),
            'gr_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'db_column': "'co_gr_id'", 'blank': 'True'}),
            'id': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True', 'db_column': "'co_id'"}),
            'locations': ('django.db.models.fields.CharField', [], {'max_length': '200', 'db_column': "'co_lo_id'", 'blank': 'True'}),
            'online': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'db_column': "'co_online'", 'blank': 'True'})
        },
        u'sherpa2.folder': {
            'Meta': {'object_name': 'Folder', 'db_table': "u'folder'"},
            'clickable': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'db_column': "'fo_clickable'", 'blank': 'True'}),
            'cols': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'db_column': "'fo_cols'", 'blank': 'True'}),
            'content': ('django.db.models.fields.TextField', [], {'db_column': "'fo_content'", 'blank': 'True'}),
            'id': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True', 'db_column': "'fo_id'"}),
            'in_menu': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'db_column': "'fo_in_menu'", 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'db_column': "'fo_name'", 'blank': 'True'}),
            'online': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'db_column': "'fo_online'", 'blank': 'True'}),
            'owner': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'db_column': "'fo_owner'", 'blank': 'True'}),
            'parent': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'db_column': "'fo_parent'", 'blank': 'True'}),
            'path': ('django.db.models.fields.CharField', [], {'max_length': '100', 'db_column': "'fo_path'", 'blank': 'True'}),
            'sequence': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'db_column': "'fo_sequence'", 'blank': 'True'}),
            'show_rel_articles': ('django.db.models.fields.IntegerField', [], {'db_column': "'fo_show_rel_articles'"}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '20', 'db_column': "'fo_status'", 'blank': 'True'}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_column': "'fo_url'", 'blank': 'True'})
        },
        u'sherpa2.folderarticle': {
            'Meta': {'object_name': 'FolderArticle', 'db_table': "u'folder_article'"},
            'article': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['sherpa2.Article']", 'db_column': "'ar_id'"}),
            'folder': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['sherpa2.Folder']", 'db_column': "'fo_id'"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '20', 'db_column': "'fa_status'", 'blank': 'True'})
        },
        u'sherpa2.fylker': {
            'Meta': {'object_name': 'Fylker', 'db_table': "u'fylker'"},
            'area': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'fylkesnr': ('django.db.models.fields.SmallIntegerField', [], {'null': 'True'}),
            'gid': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
            'navn': ('django.db.models.fields.CharField', [], {'max_length': '60'}),
            'objtype': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'perimeter': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'the_geom': ('django.contrib.gis.db.models.fields.MultiPolygonField', [], {})
        },
        u'sherpa2.kommuner': {
            'Meta': {'object_name': 'Kommuner', 'db_table': "u'kommuner'"},
            'area': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'gid': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
            'komm': ('django.db.models.fields.SmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'navn': ('django.db.models.fields.CharField', [], {'max_length': '60', 'blank': 'True'}),
            'objtype': ('django.db.models.fields.CharField', [], {'max_length': '32', 'blank': 'True'}),
            'oppdatdato': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'perimeter': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'the_geom': ('django.contrib.gis.db.models.fields.MultiPolygonField', [], {})
        },
        u'sherpa2.location': {
            'Meta': {'object_name': 'Location', 'db_table': "u'location2'"},
            'album': ('django.db.models.fields.TextField', [], {'db_column': "'lo_album'"}),
            'alias': ('django.db.models.fields.TextField', [], {'db_column': "'lo_alias'"}),
            'code': ('django.db.models.fields.TextField', [], {'db_column': "'lo_code'"}),
            'content_eng': ('django.db.models.fields.TextField', [], {'db_column': "'lo_content_eng'"}),
            'content_fre': ('django.db.models.fields.TextField', [], {'db_column': "'lo_content_fre'"}),
            'content_ger': ('django.db.models.fields.TextField', [], {'db_column': "'lo_content_ger'"}),
            'content_nno': ('django.db.models.fields.TextField', [], {'db_column': "'lo_content_nno'"}),
            'content_nor': ('django.db.models.fields.TextField', [], {'db_column': "'lo_content_nor'"}),
            'coordinates': ('django.db.models.fields.TextField', [], {'db_column': "'lo_coordinates'"}),
            'county': ('django.db.models.fields.TextField', [], {'db_column': "'lo_county'"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'db_column': "'lo_created'"}),
            'created_by': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'db_column': "'lo_created_by'"}),
            'id': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True', 'db_column': "'lo_id'"}),
            'maintainer': ('django.db.models.fields.TextField', [], {'db_column': "'lo_maintainer'"}),
            'maps': ('django.db.models.fields.TextField', [], {'db_column': "'lo_maps'"}),
            'mapshop': ('django.db.models.fields.TextField', [], {'db_column': "'lo_mapshop'"}),
            'meta': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'db_column': "'lo_meta'"}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'db_column': "'lo_modified'"}),
            'modified_by': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'db_column': "'lo_modified_by'"}),
            'municipality': ('django.db.models.fields.TextField', [], {'db_column': "'lo_municipality'"}),
            'name': ('django.db.models.fields.TextField', [], {'db_column': "'lo_name'"}),
            'online': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'db_column': "'lo_online'"}),
            'order': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'db_column': "'lo_order'"}),
            'parent': ('django.db.models.fields.TextField', [], {'db_column': "'lo_parent'"}),
            'terrain': ('django.db.models.fields.TextField', [], {'db_column': "'lo_terrain'"}),
            'the_geom': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'yr_url': ('django.db.models.fields.TextField', [], {'db_column': "'lo_yr_url'"})
        }
    }

    complete_apps = ['sherpa2', 'core']
    symmetrical = True
