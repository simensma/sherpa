# encoding: utf-8
import datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models, connection, transaction

class Migration(DataMigration):

    depends_on = (
        ("user", "0004_auto__del_field_zipcode_location"),
    )

    def forwards(self, orm):
        cursor = connection.cursor()
        cursor.execute("ALTER TABLE user_zipcode RENAME TO core_zipcode")
        cursor.execute("ALTER SEQUENCE user_zipcode_id_seq RENAME TO core_zipcode_id_seq")
        cursor.execute("UPDATE django_content_type SET app_label='core' WHERE name='zipcode'")
        cursor.execute("ALTER TABLE user_county RENAME TO core_county")
        cursor.execute("ALTER SEQUENCE user_county_id_seq RENAME TO core_county_id_seq")
        cursor.execute("UPDATE django_content_type SET app_label='core' WHERE name='county'")
        cursor.execute("ALTER TABLE user_focuscountry RENAME TO core_focuscountry")
        cursor.execute("ALTER SEQUENCE user_focuscountry_id_seq RENAME TO core_focuscountry_id_seq")
        cursor.execute("UPDATE django_content_type SET app_label='core' WHERE name='focus country'")
        transaction.commit_unless_managed()

    def backwards(self, orm):
        cursor = connection.cursor()
        cursor.execute("ALTER TABLE core_zipcode RENAME TO user_zipcode")
        cursor.execute("ALTER SEQUENCE core_zipcode_id_seq RENAME TO user_zipcode_id_seq")
        cursor.execute("UPDATE django_content_type SET app_label='user' WHERE name='zipcode'")
        cursor.execute("ALTER TABLE core_county RENAME TO user_county")
        cursor.execute("ALTER SEQUENCE core_county_id_seq RENAME TO user_county_id_seq")
        cursor.execute("UPDATE django_content_type SET app_label='user' WHERE name='county'")
        cursor.execute("ALTER TABLE core_focuscountry RENAME TO user_focuscountry")
        cursor.execute("ALTER SEQUENCE core_focuscountry_id_seq RENAME TO user_focuscountry_id_seq")
        cursor.execute("UPDATE django_content_type SET app_label='user' WHERE name='focus country'")
        transaction.commit_unless_managed()

    models = {
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
        'sites.site': {
            'Meta': {'ordering': "('domain',)", 'object_name': 'Site', 'db_table': "'django_site'"},
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['core']
