# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'FocusActType'
        db.create_table(u'ActType', (
            ('type', self.gf('django.db.models.fields.CharField')(max_length=1, primary_key=True, db_column=u'ActType')),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50, db_column=u'ActNm')),
            ('next', self.gf('django.db.models.fields.IntegerField')(db_column=u'NextNo')),
            ('last', self.gf('django.db.models.fields.IntegerField')(db_column=u'LastNo')),
        ))
        db.send_create_signal('user', ['FocusActType'])

        # Adding model 'FocusUser'
        db.create_table(u'CustTurist_members', (
            ('tempid', self.gf('django.db.models.fields.FloatField')(default=None, null=True, db_column=u'tempID')),
            ('member_id', self.gf('django.db.models.fields.IntegerField')(primary_key=True, db_column=u'memberID')),
            ('last_name', self.gf('django.db.models.fields.CharField')(max_length=255, db_column=u'Lastname')),
            ('first_name', self.gf('django.db.models.fields.CharField')(max_length=255, db_column=u'Firstname')),
            ('dob', self.gf('django.db.models.fields.DateTimeField')(db_column=u'Birthdate')),
            ('gender', self.gf('django.db.models.fields.CharField')(max_length=1, db_column=u'Gender')),
            ('linked_to', self.gf('django.db.models.fields.CharField')(max_length=255, db_column=u'LinkedTo')),
            ('enlisted_by', self.gf('django.db.models.fields.CharField')(default=0, max_length=255, db_column=u'EnlistedBy')),
            ('enlisted_article', self.gf('django.db.models.fields.CharField')(default=None, max_length=255, db_column=u'EnlistedArticle')),
            ('adr1', self.gf('django.db.models.fields.CharField')(max_length=255, db_column=u'Adr1')),
            ('adr2', self.gf('django.db.models.fields.CharField')(max_length=255, db_column=u'Adr2')),
            ('adr3', self.gf('django.db.models.fields.CharField')(max_length=255, db_column=u'Adr3')),
            ('country', self.gf('django.db.models.fields.CharField')(max_length=255, db_column=u'Country')),
            ('phone', self.gf('django.db.models.fields.CharField')(max_length=255, db_column=u'Phone')),
            ('email', self.gf('django.db.models.fields.TextField')(db_column=u'Email')),
            ('receive_yearbook', self.gf('django.db.models.fields.BooleanField')(default=False, db_column=u'ReceiveYearbook')),
            ('type', self.gf('django.db.models.fields.FloatField')(db_column=u'Type')),
            ('yearbook', self.gf('django.db.models.fields.CharField')(max_length=255, db_column=u'Yearbook')),
            ('payment_method', self.gf('django.db.models.fields.FloatField')(db_column=u'Paymethod')),
            ('contract_giro', self.gf('django.db.models.fields.BooleanField')(default=False, db_column=u'ContractGiro')),
            ('mob', self.gf('django.db.models.fields.CharField')(max_length=255, db_column=u'Mob')),
            ('postnr', self.gf('django.db.models.fields.CharField')(max_length=255, db_column=u'Postnr')),
            ('poststed', self.gf('django.db.models.fields.CharField')(max_length=255, db_column=u'Poststed')),
            ('language', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('totalprice', self.gf('django.db.models.fields.FloatField')(db_column=u'TotalPrice')),
            ('payed', self.gf('django.db.models.fields.BooleanField')(default=False, db_column=u'Payed')),
            ('reg_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, db_column=u'Regdate', blank=True)),
            ('receive_email', self.gf('django.db.models.fields.BooleanField')(default=True, db_column=u'ReceiveEmail')),
            ('receive_sms', self.gf('django.db.models.fields.BooleanField')(default=True, db_column=u'ReceiveSms')),
            ('submitted_by', self.gf('django.db.models.fields.CharField')(default=None, max_length=255, null=True, db_column=u'SubmittedBy')),
            ('submitted_date', self.gf('django.db.models.fields.DateTimeField')(default=None, null=True, db_column=u'SubmittedDt')),
            ('updated_card', self.gf('django.db.models.fields.BooleanField')(default=False, db_column=u'UpdatedCard')),
        ))
        db.send_create_signal('user', ['FocusUser'])

        # Adding model 'FocusCountry'
        db.create_table('user_focuscountry', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('code', self.gf('django.db.models.fields.CharField')(max_length=2)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('user', ['FocusCountry'])


    def backwards(self, orm):
        
        # Deleting model 'FocusActType'
        db.delete_table(u'ActType')

        # Deleting model 'FocusUser'
        db.delete_table(u'CustTurist_members')

        # Deleting model 'FocusCountry'
        db.delete_table('user_focuscountry')


    models = {
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
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2012, 5, 21, 16, 55, 56, 280808)'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2012, 5, 21, 16, 55, 56, 280638)'}),
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
        'user.county': {
            'Meta': {'object_name': 'County'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'user.focusacttype': {
            'Meta': {'object_name': 'FocusActType', 'db_table': "u'ActType'"},
            'last': ('django.db.models.fields.IntegerField', [], {'db_column': "u'LastNo'"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_column': "u'ActNm'"}),
            'next': ('django.db.models.fields.IntegerField', [], {'db_column': "u'NextNo'"}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '1', 'primary_key': 'True', 'db_column': "u'ActType'"})
        },
        'user.focuscountry': {
            'Meta': {'object_name': 'FocusCountry'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'user.focususer': {
            'Meta': {'object_name': 'FocusUser', 'db_table': "u'CustTurist_members'"},
            'adr1': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_column': "u'Adr1'"}),
            'adr2': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_column': "u'Adr2'"}),
            'adr3': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_column': "u'Adr3'"}),
            'contract_giro': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_column': "u'ContractGiro'"}),
            'country': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_column': "u'Country'"}),
            'dob': ('django.db.models.fields.DateTimeField', [], {'db_column': "u'Birthdate'"}),
            'email': ('django.db.models.fields.TextField', [], {'db_column': "u'Email'"}),
            'enlisted_article': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '255', 'db_column': "u'EnlistedArticle'"}),
            'enlisted_by': ('django.db.models.fields.CharField', [], {'default': '0', 'max_length': '255', 'db_column': "u'EnlistedBy'"}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_column': "u'Firstname'"}),
            'gender': ('django.db.models.fields.CharField', [], {'max_length': '1', 'db_column': "u'Gender'"}),
            'language': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_column': "u'Lastname'"}),
            'linked_to': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_column': "u'LinkedTo'"}),
            'member_id': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True', 'db_column': "u'memberID'"}),
            'mob': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_column': "u'Mob'"}),
            'payed': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_column': "u'Payed'"}),
            'payment_method': ('django.db.models.fields.FloatField', [], {'db_column': "u'Paymethod'"}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_column': "u'Phone'"}),
            'postnr': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_column': "u'Postnr'"}),
            'poststed': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_column': "u'Poststed'"}),
            'receive_email': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'db_column': "u'ReceiveEmail'"}),
            'receive_sms': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'db_column': "u'ReceiveSms'"}),
            'receive_yearbook': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_column': "u'ReceiveYearbook'"}),
            'reg_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'db_column': "u'Regdate'", 'blank': 'True'}),
            'submitted_by': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '255', 'null': 'True', 'db_column': "u'SubmittedBy'"}),
            'submitted_date': ('django.db.models.fields.DateTimeField', [], {'default': 'None', 'null': 'True', 'db_column': "u'SubmittedDt'"}),
            'tempid': ('django.db.models.fields.FloatField', [], {'default': 'None', 'null': 'True', 'db_column': "u'tempID'"}),
            'totalprice': ('django.db.models.fields.FloatField', [], {'db_column': "u'TotalPrice'"}),
            'type': ('django.db.models.fields.FloatField', [], {'db_column': "u'Type'"}),
            'updated_card': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_column': "u'UpdatedCard'"}),
            'yearbook': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_column': "u'Yearbook'"})
        },
        'user.profile': {
            'Meta': {'object_name': 'Profile'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'text': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.User']", 'unique': 'True'})
        },
        'user.zipcode': {
            'Meta': {'object_name': 'Zipcode'},
            'city': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'city_code': ('django.db.models.fields.CharField', [], {'max_length': '4'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'location': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'zip_code': ('django.db.models.fields.CharField', [], {'max_length': '4'})
        }
    }

    complete_apps = ['user']
