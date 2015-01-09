# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models

class Migration(DataMigration):

    def forwards(self, orm):
        redirects = [
            ('140', 'http://www2.turistforeningen.no/index.php?fo_id=6007'),
            ('aretsgave', 'http://www2.turistforeningen.no/aretsgave.php'),
            ('butikk', 'http://www2.turistforeningen.no/index.php?fo_id=435'),
            ('daltilfjell', 'http://www2.turistforeningen.no/article.php?ar_id=11201'),
            ('endeligmedlem', 'http://www2.turistforeningen.no/files/DNT/Endelig%%20medlem'),
            ('engerdalogtrysil', 'http://www2.turistforeningen.no/group.php?gr_id=16&fo_id=128'),
            ('evaluering', 'http://response.questback.com/DenNorskeTuristforening/landsmotet2005/'),
            ('faktaark', 'http://www2.turistforeningen.no/files/DNT/Intranett/Faktaark/'),
            ('film', 'http://www2.turistforeningen.no/article.php?ar_id=11194&fo_id=15'),
            ('fjellfest', 'http://www2.turistforeningen.no/article.php?ar_id=8152&fo_id=15'),
            ('fjellfesten', 'http://www2.turistforeningen.no/article.php?ar_id=8152&fo_id=15'),
            ('fjellforing', 'http://www.dntfjellsport.no/index.php?fo_id=176'),
            ('fjellogviddespesial', 'http://www.calameo.com/read/0002483005e90ae80224e'),
            ('fjellvett', 'http://www2.turistforeningen.no/index.php?fo_id=184'),
            ('gaver', 'http://www2.turistforeningen.no/index.php?fo_id=3160'),
            ('grensesommen', 'http://www2.turistforeningen.no/turplanlegger/trip.php?ac_id=7438'),
            ('hyttedrift', 'http://www2.turistforeningen.no/index.php?fo_id=4883'),
            ('intranett', 'http://foreningsnett.turistforeningen.no/'),
            ('ist', 'http://www.istur.no/'),
            ('kvistekart', '/vintermerking/'),
            ('lokalmat', 'http://www2.turistforeningen.no/index.php?fo_id=2049'),
            ('marked', 'http://www2.turistforeningen.no/classified.php'),
            ('markedsplassen', 'http://www2.turistforeningen.no/classified.php'),
            ('membership', 'http://www2.turistforeningen.no/english/index.php?fo_id=3606'),
            ('nettbutikk', 'http://www.dntbutikken.no/'),
            ('internbutikk', 'http://internbutikk.turistforeningen.no/eshop/'),
            ('paaske', 'http://www2.turistforeningen.no/article.php?ar_id=7473'),
            ('pressearkiv', 'http://www2.turistforeningen.no/pressearkiv/'),
            ('profil', 'http://foreningsnett.turistforeningen.no/file.php?dir=/Kommunikasjon/Profilprogram&fo_id=6691'),
            ('profilprogram', 'http://foreningsnett.turistforeningen.no/file.php?dir=/Kommunikasjon/Profilprogram&fo_id=6691'),
            ('ruteinntegning', 'http://www2.turistforeningen.no/ruteinntegning.pdf'),
            ('skred', 'http://www2.turistforeningen.no/article.php?ar_id=6285&fo_id=2714'),
            ('sor-varanger', 'http://www2.turistforeningen.no/group.php?gr_id=48&fo_id=128'),
            ('sotajazz', 'http://www2.turistforeningen.no/article.php?ar_id=8151&fo_id=2419'),
            ('telenorbarn', 'http://www2.turistforeningen.no/form2.php?form=telenorbarn'),
            ('tester', 'http://www2.turistforeningen.no/index.php?fo_id=2771'),
            ('turbosvar', 'http://response.questback.com/dennorsketuristforening/ud57ujnxnk/'),
            ('varanger', 'http://www2.turistforeningen.no/group.php?gr_id=51&fo_id=128'),
            ('skredkurs', 'http://www2.turistforeningen.no/activity.php?ac_cat=skredkurs&fo_id=9024'),
            ('matogreise', 'http://www.matogreiseliv.no'),
            ('francaise', 'http://www2.turistforeningen.no/francais/'),
            ('kartbutikken', 'http://www.dntbutikken.no/'),
            ('kartbutikk', 'http://www.dntbutikken.no/'),
            ('skolecamp', 'http://www.skolecamp.no/'),
            ('buss', 'http://www.turistforeningen.no/article.php?ar_id=10549&fo_id=311'),
            ('engerdalogtrysil', 'http://www2.turistforeningen.no/group.php?gr_id=16&fo_id=128'),
            ('medlemsfordeler', 'http://www2.turistforeningen.no/index.php?fo_id=3814'),
            ('girofeil', 'http://www2.turistforeningen.no/article.php?ar_id=25749&fo_id=15'),
            ('donald', 'http://innmelding.turistforeningen.no'),
            ('komdegut', 'http://www.turistforeningen.no/komdegut/index.php'),
            ('singeltur', 'http://www2.turistforeningen.no/activity.php?fo_id=2513&search_string=&ac_cat=singeltur'),
            ('blogg', 'http://blogg.turistforeningen.no/'),
            ('sykkelturforslag', 'http://www.turistforeningen.no/sykkelturforslag/index.php'),
            ('fyr', 'http://www.turistforeningen.no/article.php?ar_id=27945'),
            ('hyttefoto', 'http://www.turistforeningen.no/form2.php?form=hyttebilder'),
            ('era2012', 'http://www.turistforeningen.no/english/form2.php?form=era12'),
            ('gullnokkel', 'http://www2.turistforeningen.no/index.php?fo_id=9786'),
            ('kitekurs', 'http://www2.turistforeningen.no/activity.php?ac_cat=kiting&fo_id=9893'),
        ]

        dnt = orm['core.Site'].objects.get(id=1)

        for redirect in redirects:
            redirect = orm['core.Redirect'](
                site=dnt,
                path=redirect[0],
                destination=redirect[1],
            )
            redirect.save()

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
        u'core.redirect': {
            'Meta': {'ordering': "['path']", 'object_name': 'Redirect'},
            'destination': ('django.db.models.fields.CharField', [], {'max_length': '2048'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'path': ('django.db.models.fields.CharField', [], {'max_length': '512'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'redirects'", 'to': u"orm['core.Site']"})
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
            'template_description': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '1023'}),
            'template_main': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'template_type': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255'}),
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
        u'core.zipcodestate': {
            'Meta': {'object_name': 'ZipcodeState'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_update': ('django.db.models.fields.DateTimeField', [], {})
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

    complete_apps = ['core']
    symmetrical = True
