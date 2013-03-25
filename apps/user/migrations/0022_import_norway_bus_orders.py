# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models

class Migration(DataMigration):

    def forwards(self, orm):
        for old_ticket in orm['sherpa25.Norway'].objects.all():
            new_ticket = orm['user.NorwayBusTicketOld'](
                memberid=old_ticket.memberid,
                date_placed=old_ticket.date_placed,
                date_trip_text=old_ticket.date_trip_text,
                distance=old_ticket.distance)
            new_ticket.save()

    def backwards(self, orm):
        pass

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
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'children'", 'null': 'True', 'to': "orm['association.Association']"}),
            'phone': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255'}),
            'post_address': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255'}),
            'site': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['core.Site']", 'unique': 'True', 'null': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'visit_address': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255'}),
            'zipcode': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Zipcode']", 'null': 'True'})
        },
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'core.county': {
            'Meta': {'object_name': 'County'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'core.site': {
            'Meta': {'object_name': 'Site'},
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'prefix': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'template': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.SiteTemplate']"})
        },
        'core.sitetemplate': {
            'Meta': {'object_name': 'SiteTemplate'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'core.zipcode': {
            'Meta': {'object_name': 'Zipcode'},
            'area': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'city_code': ('django.db.models.fields.CharField', [], {'max_length': '4'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'zipcode': ('django.db.models.fields.CharField', [], {'max_length': '4'})
        },
        'sherpa25.classified': {
            'Meta': {'object_name': 'Classified', 'db_table': "u'Classified'"},
            'authorized': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'content': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'county': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'online': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.TextField', [], {'blank': 'True'})
        },
        'sherpa25.classifiedimage': {
            'Meta': {'object_name': 'ClassifiedImage', 'db_table': "u'ClassifiedImage'"},
            'created': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'online': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'path': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'status': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        'sherpa25.link': {
            'Meta': {'object_name': 'Link', 'db_table': "u'Link'"},
            'fromid': ('django.db.models.fields.IntegerField', [], {'db_column': "'fromId'"}),
            'fromobject': ('django.db.models.fields.TextField', [], {'db_column': "'fromObject'"}),
            'id': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
            'priority': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'role': ('django.db.models.fields.IntegerField', [], {}),
            'toid': ('django.db.models.fields.IntegerField', [], {'db_column': "'toId'"}),
            'toobject': ('django.db.models.fields.TextField', [], {'db_column': "'toObject'"})
        },
        'sherpa25.member': {
            'Meta': {'object_name': 'Member', 'db_table': "u'Member'"},
            'address1': ('django.db.models.fields.TextField', [], {}),
            'address2': ('django.db.models.fields.TextField', [], {}),
            'address3': ('django.db.models.fields.TextField', [], {}),
            'birthdate': ('django.db.models.fields.DateField', [], {'null': 'True', 'db_column': "'birthDate'"}),
            'cellphone': ('django.db.models.fields.TextField', [], {'db_column': "'cellPhone'"}),
            'countrycode': ('django.db.models.fields.TextField', [], {'db_column': "'countryCode'"}),
            'countryname': ('django.db.models.fields.TextField', [], {'db_column': "'countryName'"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'email': ('django.db.models.fields.TextField', [], {}),
            'first_name': ('django.db.models.fields.TextField', [], {'db_column': "'firstName'"}),
            'gender': ('django.db.models.fields.CharField', [], {'max_length': '1', 'db_column': "'sex'"}),
            'homephone': ('django.db.models.fields.TextField', [], {'db_column': "'homePhone'"}),
            'id': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
            'last_name': ('django.db.models.fields.TextField', [], {'db_column': "'lastName'"}),
            'membercurrentbalance': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'db_column': "'memberCurrentBalance'"}),
            'membergroupid': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'db_column': "'memberGroupId'"}),
            'membergroupname': ('django.db.models.fields.TextField', [], {'db_column': "'memberGroupName'"}),
            'memberid': ('django.db.models.fields.IntegerField', [], {'unique': 'True', 'null': 'True', 'db_column': "'memberId'"}),
            'memberinvoicetype': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'db_column': "'memberInvoiceType'"}),
            'memberparent': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'db_column': "'memberParent'"}),
            'memberpreviousbalance': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'db_column': "'memberPreviousBalance'"}),
            'memberrecruiter': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'db_column': "'memberRecruiter'"}),
            'memberservices': ('django.db.models.fields.TextField', [], {'db_column': "'memberServices'"}),
            'memberstartdate': ('django.db.models.fields.DateField', [], {'null': 'True', 'db_column': "'memberStartDate'"}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'online': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'password': ('django.db.models.fields.TextField', [], {}),
            'receiveemail': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_column': "'receiveEmail'"}),
            'receivesms': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_column': "'receiveSms'"}),
            'status': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'workphone': ('django.db.models.fields.TextField', [], {'db_column': "'workPhone'"}),
            'ziparea': ('django.db.models.fields.TextField', [], {'db_column': "'zipArea'"}),
            'zipcode': ('django.db.models.fields.TextField', [], {'db_column': "'zipCode'"})
        },
        'sherpa25.norway': {
            'Meta': {'object_name': 'Norway', 'db_table': "u'Norway'"},
            'address1': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'address2': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'cellphone': ('django.db.models.fields.TextField', [], {'db_column': "'cellPhone'"}),
            'countrycode': ('django.db.models.fields.CharField', [], {'max_length': '20', 'db_column': "'countryCode'"}),
            'date_placed': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'db_column': "'registerDate'"}),
            'date_trip_text': ('django.db.models.fields.CharField', [], {'max_length': '25', 'db_column': "'tripDate'"}),
            'distance': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_column': "'tripStretch'"}),
            'email': ('django.db.models.fields.TextField', [], {}),
            'homephone': ('django.db.models.fields.TextField', [], {'db_column': "'homePhone'"}),
            'memberid': ('django.db.models.fields.IntegerField', [], {'unique': 'True', 'db_column': "'memberId'"}),
            'membername': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_column': "'memberName'"}),
            'orderid': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True', 'db_column': "'orderId'"}),
            'workphone': ('django.db.models.fields.TextField', [], {'db_column': "'workPhone'"}),
            'ziparea': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_column': "'zipArea'"}),
            'zipcode': ('django.db.models.fields.CharField', [], {'max_length': '20', 'db_column': "'zipCode'"})
        },
        'user.associationrole': {
            'Meta': {'object_name': 'AssociationRole'},
            'association': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['association.Association']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'profile': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['user.Profile']"}),
            'role': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'user.norwaybusticket': {
            'Meta': {'object_name': 'NorwayBusTicket'},
            'date_placed': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_trip': ('django.db.models.fields.DateTimeField', [], {}),
            'distance': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'profile': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'norway_bus_ticket'", 'unique': 'True', 'to': "orm['user.Profile']"})
        },
        'user.norwaybusticketold': {
            'Meta': {'object_name': 'NorwayBusTicketOld'},
            'date_placed': ('django.db.models.fields.DateTimeField', [], {}),
            'date_trip_text': ('django.db.models.fields.CharField', [], {'max_length': '25'}),
            'distance': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'memberid': ('django.db.models.fields.IntegerField', [], {'unique': 'True'})
        },
        'user.profile': {
            'Meta': {'object_name': 'Profile'},
            'associations': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'users'", 'symmetrical': 'False', 'through': "orm['user.AssociationRole']", 'to': "orm['association.Association']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'memberid': ('django.db.models.fields.IntegerField', [], {'unique': 'True', 'null': 'True'}),
            'password_restore_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'password_restore_key': ('django.db.models.fields.CharField', [], {'max_length': '40', 'null': 'True'}),
            'sherpa_email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.User']", 'unique': 'True'})
        }
    }

    complete_apps = ['sherpa25', 'user']
    symmetrical = True
