# encoding: utf-8
import datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models

class Migration(DataMigration):

    def forwards(self, orm):
        for s2a in orm['sherpa2.Association'].objects.all().order_by('parent', 'id'):
            # These are some "hacks" and cleanup based on the current state of the S2 DB.

            # Check type first - some will be skipped (yeah, in code, whatever, this isn't that large of a query and only runs once)
            group_type = ''
            if s2a.type == '':
                continue
            elif s2a.type == '|Annen':
                continue
            elif s2a.type == '|Barn':
                type = 'turgruppe'
                group_type = 'barn'
            elif s2a.type == '|Ekstern':
                continue
            elif s2a.type == '|Fjellsport':
                # Special case for central group
                if s2a.id == 60:
                    type = 'sentral'
                else:
                    type = 'turgruppe'
                group_type = 'fjellsport'
            elif s2a.type == '|Hovedforening':
                type = 'forening'
            elif s2a.type == '|Hytte':
                continue
            elif s2a.type == u'|NF-arrangør':
                continue
            elif s2a.type == '|Prosjekt':
                continue
            elif s2a.type == '|Senior':
                type = 'turgruppe'
                group_type = 'senior'
            elif s2a.type == '|Sentral':
                type = 'sentral'
            elif s2a.type == '|Skole':
                continue
            elif s2a.type == '|Styre':
                continue
            elif s2a.type == '|Underforening':
                type = 'turlag'
            elif s2a.type == '|Ungdom':
                # Special case for central group
                if s2a.id == 1180:
                    type = 'sentral'
                else:
                    type = 'turgruppe'

                # Special-case: Skip the middle 'project'-group
                if s2a.id == 193:
                    s2a.parent = 6
                group_type = 'ung'

            # Use the same ID
            id = s2a.id
            name = s2a.name.strip()

            # Lagre som int og gå igjennom etterpå
            parent = s2a.parent
            if parent == 0:
                parent = None
            else:
                parent = orm['association.Association'].objects.get(id=parent)

            focus_id = s2a.focus_id
            if focus_id == 0:
                focus_id = None

            post_address = s2a.post_address.strip()
            visit_address = s2a.visit_address.strip()

            # Zip:
            zipcode = s2a.zipcode.strip()
            if zipcode == '':
                zipcode = None
            else:
                if zipcode.startswith('N-'):
                    zipcode = zipcode[2:]
                zipcode = orm['core.Zipcode'].objects.get(zipcode=zipcode[:4])

            phone = s2a.phone
            email = s2a.email
            organization_no = s2a.orgnr
            if organization_no == None:
                organization_no = ''

            gmap_url = s2a.map
            if gmap_url == None:
                gmap_url = ''

            facebook_url = s2a.facebook
            if facebook_url == None:
                facebook_url = ''

            a = orm['association.Association'](
                id=id,
                name=name,
                parent=parent,
                focus_id=focus_id,
                type=type,
                group_type=group_type,
                post_address=post_address,
                visit_address=visit_address,
                zipcode=zipcode,
                phone=phone,
                email=email,
                organization_no=organization_no,
                gmap_url=gmap_url,
                facebook_url=facebook_url)

            a.save()

            # ManyToManyFields, add after creating object
            county = s2a.county
            if county != '' and county != None:
                a.counties = orm['core.County'].objects.filter(sherpa_id__in=county.split("|"))



    def backwards(self, orm):
        print("Warning: Skipping irreversible migration - import of associations.")


    models = {
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
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['association.Association']", 'null': 'True'}),
            'phone': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255'}),
            'post_address': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'visit_address': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255'}),
            'zipcode': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Zipcode']", 'null': 'True'})
        },
        'core.county': {
            'Meta': {'object_name': 'County'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'sherpa_id': ('django.db.models.fields.IntegerField', [], {'null': 'True'})
        },
        'core.focuscountry': {
            'Meta': {'object_name': 'FocusCountry'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'scandinavian': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'core.search': {
            'Meta': {'object_name': 'Search'},
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'query': ('django.db.models.fields.CharField', [], {'max_length': '1024'})
        },
        'core.sitedetails': {
            'Meta': {'object_name': 'SiteDetails'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'prefix': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'site': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'details'", 'unique': 'True', 'to': "orm['sites.Site']"}),
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
        'sherpa2.association': {
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
        'sherpa2.cabin': {
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
            'the_geom': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'type': ('django.db.models.fields.TextField', [], {'db_column': "u'ca_type'", 'blank': 'True'}),
            'url': ('django.db.models.fields.TextField', [], {'db_column': "u'ca_url'", 'blank': 'True'}),
            'url_ut': ('django.db.models.fields.TextField', [], {'db_column': "u'ca_url_ut'", 'blank': 'True'}),
            'utm': ('django.db.models.fields.TextField', [], {'db_column': "u'ca_utm'", 'blank': 'True'}),
            'utm_gps': ('django.db.models.fields.TextField', [], {'db_column': "u'ca_utm_gps'", 'blank': 'True'}),
            'yr_url': ('django.db.models.fields.TextField', [], {'db_column': "u'ca_yr_url'", 'blank': 'True'})
        },
        'sites.site': {
            'Meta': {'ordering': "('domain',)", 'object_name': 'Site', 'db_table': "'django_site'"},
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['sherpa2', 'core', 'association']
