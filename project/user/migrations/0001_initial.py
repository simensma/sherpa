# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Profile'
        db.create_table('user_profile', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['auth.User'], unique=True)),
            ('phone', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('password_restore_key', self.gf('django.db.models.fields.CharField')(max_length=40, unique=True, null=True)),
            ('password_restore_date', self.gf('django.db.models.fields.DateTimeField')(null=True)),
        ))
        db.send_create_signal('user', ['Profile'])

        # Adding model 'Zipcode'
        db.create_table('user_zipcode', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('zipcode', self.gf('django.db.models.fields.CharField')(max_length=4)),
            ('location', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('city_code', self.gf('django.db.models.fields.CharField')(max_length=4)),
            ('city', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal('user', ['Zipcode'])

        # Adding model 'County'
        db.create_table('user_county', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('code', self.gf('django.db.models.fields.CharField')(max_length=2)),
            ('sherpa_id', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal('user', ['County'])

        # Adding model 'FocusCountry'
        db.create_table('user_focuscountry', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('code', self.gf('django.db.models.fields.CharField')(max_length=2)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('scandinavian', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('user', ['FocusCountry'])

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

        # Adding model 'Actor'
        db.create_table(u'Actor', (
            ('seqno', self.gf('django.db.models.fields.AutoField')(primary_key=True, db_column=u'SeqNo')),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=50, db_column=u'Type')),
            ('actno', self.gf('django.db.models.fields.IntegerField')(db_column=u'ActNo')),
            ('last_name', self.gf('django.db.models.fields.CharField')(max_length=50, db_column=u'Nm', blank=True)),
            ('first_name', self.gf('django.db.models.fields.CharField')(max_length=50, db_column=u'FiNm', blank=True)),
            ('birth_date', self.gf('django.db.models.fields.DateTimeField')(null=True, db_column=u'BDt', blank=True)),
            ('pno', self.gf('django.db.models.fields.CharField')(max_length=50, db_column=u'PNo', blank=True)),
            ('sex', self.gf('django.db.models.fields.CharField')(max_length=1, db_column=u'Sex', blank=True)),
            ('orgno', self.gf('django.db.models.fields.CharField')(max_length=50, db_column=u'OrgNo', blank=True)),
            ('ph', self.gf('django.db.models.fields.CharField')(max_length=50, db_column=u'Ph', blank=True)),
            ('fax', self.gf('django.db.models.fields.CharField')(max_length=50, db_column=u'Fax', blank=True)),
            ('mobph', self.gf('django.db.models.fields.CharField')(max_length=50, db_column=u'MobPh', blank=True)),
            ('email', self.gf('django.db.models.fields.CharField')(max_length=250, db_column=u'EMail', blank=True)),
            ('web', self.gf('django.db.models.fields.CharField')(max_length=250, db_column=u'Web', blank=True)),
            ('adtype', self.gf('django.db.models.fields.CharField')(max_length=3, db_column=u'AdType', blank=True)),
            ('note1', self.gf('django.db.models.fields.TextField')(db_column=u'Note1', blank=True)),
            ('note2', self.gf('django.db.models.fields.TextField')(db_column=u'Note2', blank=True)),
            ('startdt', self.gf('django.db.models.fields.DateTimeField')(null=True, db_column=u'StartDt', blank=True)),
            ('startcd', self.gf('django.db.models.fields.CharField')(max_length=5, db_column=u'StartCd', blank=True)),
            ('enddt', self.gf('django.db.models.fields.DateTimeField')(null=True, db_column=u'EndDt', blank=True)),
            ('endcd', self.gf('django.db.models.fields.CharField')(max_length=5, db_column=u'EndCd', blank=True)),
            ('payterm', self.gf('django.db.models.fields.IntegerField')(db_column=u'PayTerm')),
            ('accno', self.gf('django.db.models.fields.CharField')(max_length=50, db_column=u'AccNo', blank=True)),
            ('disc', self.gf('django.db.models.fields.SmallIntegerField')(null=True, db_column=u'Disc', blank=True)),
            ('vatcd', self.gf('django.db.models.fields.BooleanField')(default=False, db_column=u'VatCd')),
            ('optint1', self.gf('django.db.models.fields.IntegerField')(db_column=u'OptInt1')),
            ('optint2', self.gf('django.db.models.fields.IntegerField')(db_column=u'OptInt2')),
            ('optint3', self.gf('django.db.models.fields.IntegerField')(db_column=u'OptInt3')),
            ('optint4', self.gf('django.db.models.fields.IntegerField')(db_column=u'OptInt4')),
            ('optint5', self.gf('django.db.models.fields.IntegerField')(db_column=u'OptInt5')),
            ('optint6', self.gf('django.db.models.fields.IntegerField')(db_column=u'OptInt6')),
            ('optint7', self.gf('django.db.models.fields.IntegerField')(db_column=u'OptInt7')),
            ('optint8', self.gf('django.db.models.fields.IntegerField')(db_column=u'OptInt8')),
            ('optint9', self.gf('django.db.models.fields.IntegerField')(db_column=u'OptInt9')),
            ('optchar1', self.gf('django.db.models.fields.CharField')(max_length=10, db_column=u'OptChar1', blank=True)),
            ('optchar2', self.gf('django.db.models.fields.CharField')(max_length=10, db_column=u'OptChar2', blank=True)),
            ('optchar3', self.gf('django.db.models.fields.CharField')(max_length=10, db_column=u'OptChar3', blank=True)),
            ('optchar4', self.gf('django.db.models.fields.CharField')(max_length=10, db_column=u'OptChar4', blank=True)),
            ('optchar5', self.gf('django.db.models.fields.CharField')(max_length=10, db_column=u'OptChar5', blank=True)),
            ('optchar6', self.gf('django.db.models.fields.CharField')(max_length=10, db_column=u'OptChar6', blank=True)),
            ('optchar7', self.gf('django.db.models.fields.CharField')(max_length=10, db_column=u'OptChar7', blank=True)),
            ('optchar8', self.gf('django.db.models.fields.CharField')(max_length=10, db_column=u'OptChar8', blank=True)),
            ('optchar9', self.gf('django.db.models.fields.CharField')(max_length=10, db_column=u'OptChar9', blank=True)),
            ('optbit1', self.gf('django.db.models.fields.BooleanField')(default=False, db_column=u'OptBit1')),
            ('optbit2', self.gf('django.db.models.fields.BooleanField')(default=False, db_column=u'OptBit2')),
            ('optbit3', self.gf('django.db.models.fields.BooleanField')(default=False, db_column=u'OptBit3')),
            ('optbit4', self.gf('django.db.models.fields.BooleanField')(default=False, db_column=u'OptBit4')),
            ('optbit5', self.gf('django.db.models.fields.BooleanField')(default=False, db_column=u'OptBit5')),
            ('optbit6', self.gf('django.db.models.fields.BooleanField')(default=False, db_column=u'OptBit6')),
            ('optlng1', self.gf('django.db.models.fields.FloatField')(db_column=u'OptLng1')),
            ('optlng2', self.gf('django.db.models.fields.FloatField')(db_column=u'OptLng2')),
            ('optlng3', self.gf('django.db.models.fields.FloatField')(db_column=u'OptLng3')),
            ('optdate1', self.gf('django.db.models.fields.DateTimeField')(null=True, db_column=u'OptDate1', blank=True)),
            ('optdate2', self.gf('django.db.models.fields.DateTimeField')(null=True, db_column=u'OptDate2', blank=True)),
            ('optdate3', self.gf('django.db.models.fields.DateTimeField')(null=True, db_column=u'OptDate3', blank=True)),
            ('optdate4', self.gf('django.db.models.fields.DateTimeField')(null=True, db_column=u'OptDate4', blank=True)),
            ('county1', self.gf('django.db.models.fields.CharField')(max_length=50, db_column=u'County1', blank=True)),
            ('county2', self.gf('django.db.models.fields.CharField')(max_length=50, db_column=u'County2', blank=True)),
            ('actrel1', self.gf('django.db.models.fields.IntegerField')(db_column=u'ActRel1')),
            ('actrel2', self.gf('django.db.models.fields.IntegerField')(db_column=u'ActRel2')),
            ('actrel3', self.gf('django.db.models.fields.IntegerField')(db_column=u'ActRel3')),
            ('actrel4', self.gf('django.db.models.fields.IntegerField')(db_column=u'ActRel4')),
            ('actrel5', self.gf('django.db.models.fields.IntegerField')(db_column=u'ActRel5')),
            ('actrel6', self.gf('django.db.models.fields.IntegerField')(null=True, db_column=u'ActRel6', blank=True)),
            ('actrel7', self.gf('django.db.models.fields.IntegerField')(null=True, db_column=u'ActRel7', blank=True)),
            ('actrel8', self.gf('django.db.models.fields.IntegerField')(null=True, db_column=u'ActRel8', blank=True)),
            ('actrel9', self.gf('django.db.models.fields.IntegerField')(null=True, db_column=u'ActRel9', blank=True)),
            ('inf1', self.gf('django.db.models.fields.CharField')(max_length=50, db_column=u'Inf1', blank=True)),
            ('inf2', self.gf('django.db.models.fields.CharField')(max_length=50, db_column=u'Inf2', blank=True)),
            ('inf3', self.gf('django.db.models.fields.CharField')(max_length=50, db_column=u'Inf3', blank=True)),
            ('inf4', self.gf('django.db.models.fields.CharField')(max_length=50, db_column=u'Inf4', blank=True)),
            ('inf5', self.gf('django.db.models.fields.CharField')(max_length=50, db_column=u'Inf5', blank=True)),
            ('webusr', self.gf('django.db.models.fields.CharField')(max_length=50, db_column=u'WebUsr', blank=True)),
            ('webpw', self.gf('django.db.models.fields.CharField')(max_length=50, db_column=u'WebPw', blank=True)),
            ('websh', self.gf('django.db.models.fields.IntegerField')(db_column=u'WebSh')),
            ('weblang', self.gf('django.db.models.fields.CharField')(max_length=5, db_column=u'WebLang', blank=True)),
            ('webcrby', self.gf('django.db.models.fields.CharField')(max_length=25, db_column=u'WebCrBy', blank=True)),
            ('webcrdt', self.gf('django.db.models.fields.DateTimeField')(null=True, db_column=u'WebCrDt', blank=True)),
            ('crby', self.gf('django.db.models.fields.CharField')(max_length=25, db_column=u'CrBy')),
            ('crdt', self.gf('django.db.models.fields.DateTimeField')(db_column=u'CrDt')),
            ('chby', self.gf('django.db.models.fields.CharField')(max_length=25, db_column=u'ChBy')),
            ('chdt', self.gf('django.db.models.fields.DateTimeField')(db_column=u'ChDt')),
        ))
        db.send_create_signal('user', ['Actor'])

        # Adding model 'ActorAddress'
        db.create_table(u'ActAd', (
            ('seqno', self.gf('django.db.models.fields.AutoField')(primary_key=True, db_column=u'SeqNo')),
            ('actseqno', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['user.Actor'], unique=True, db_column=u'ActSeqNo')),
            ('actnojoin', self.gf('django.db.models.fields.IntegerField')(db_column=u'ActNoJoin')),
            ('actadtype', self.gf('django.db.models.fields.CharField')(unique=True, max_length=3, db_column=u'ActAdType', blank=True)),
            ('a1', self.gf('django.db.models.fields.CharField')(max_length=40, db_column=u'A1', blank=True)),
            ('a2', self.gf('django.db.models.fields.CharField')(max_length=40, db_column=u'A2', blank=True)),
            ('a3', self.gf('django.db.models.fields.CharField')(max_length=40, db_column=u'A3', blank=True)),
            ('zipcode', self.gf('django.db.models.fields.CharField')(max_length=9, db_column=u'PCode', blank=True)),
            ('parea', self.gf('django.db.models.fields.CharField')(max_length=30, db_column=u'PArea', blank=True)),
            ('country', self.gf('django.db.models.fields.CharField')(max_length=3, db_column=u'CtryCode', blank=True)),
            ('frdt', self.gf('django.db.models.fields.DateTimeField')(null=True, db_column=u'FrDt', blank=True)),
            ('todt', self.gf('django.db.models.fields.DateTimeField')(null=True, db_column=u'ToDt', blank=True)),
            ('chby', self.gf('django.db.models.fields.CharField')(max_length=50, db_column=u'ChBy', blank=True)),
            ('chdt', self.gf('django.db.models.fields.DateTimeField')(null=True, db_column=u'ChDt', blank=True)),
            ('crby', self.gf('django.db.models.fields.CharField')(max_length=50, db_column=u'CrBy', blank=True)),
            ('crdt', self.gf('django.db.models.fields.DateTimeField')(null=True, db_column=u'CrDt', blank=True)),
        ))
        db.send_create_signal('user', ['ActorAddress'])

        # Adding model 'FocusZipcode'
        db.create_table(u'PostalCode', (
            ('zipcode', self.gf('django.db.models.fields.CharField')(max_length=9, primary_key=True, db_column=u'PostCode')),
            ('postarea', self.gf('django.db.models.fields.CharField')(max_length=40, db_column=u'PostArea')),
            ('county1no', self.gf('django.db.models.fields.CharField')(max_length=10, db_column=u'County1No', blank=True)),
            ('county1name', self.gf('django.db.models.fields.CharField')(max_length=40, db_column=u'County1Name', blank=True)),
            ('county2no', self.gf('django.db.models.fields.CharField')(max_length=10, db_column=u'County2No', blank=True)),
            ('county2name', self.gf('django.db.models.fields.CharField')(max_length=40, db_column=u'County2Name', blank=True)),
            ('main_association_id', self.gf('django.db.models.fields.IntegerField')(null=True, db_column=u'District1', blank=True)),
            ('local_association_id', self.gf('django.db.models.fields.IntegerField')(null=True, db_column=u'District2', blank=True)),
            ('crby', self.gf('django.db.models.fields.CharField')(max_length=25, db_column=u'CrBy', blank=True)),
            ('crdt', self.gf('django.db.models.fields.DateTimeField')(null=True, db_column=u'CrDt', blank=True)),
            ('chby', self.gf('django.db.models.fields.CharField')(max_length=25, db_column=u'ChBy', blank=True)),
            ('chdt', self.gf('django.db.models.fields.DateTimeField')(null=True, db_column=u'ChDt', blank=True)),
        ))
        db.send_create_signal('user', ['FocusZipcode'])

        # Adding model 'FocusPrice'
        db.create_table(u'Cust_Turist_Region_PriceCode_CrossTable', (
            ('association_id', self.gf('django.db.models.fields.IntegerField')(primary_key=True, db_column=u'Region')),
            ('main', self.gf('django.db.models.fields.IntegerField')(null=True, db_column=u'C101', blank=True)),
            ('student', self.gf('django.db.models.fields.IntegerField')(null=True, db_column=u'C102', blank=True)),
            ('senior', self.gf('django.db.models.fields.IntegerField')(null=True, db_column=u'C103', blank=True)),
            ('lifelong', self.gf('django.db.models.fields.IntegerField')(null=True, db_column=u'C104', blank=True)),
            ('child', self.gf('django.db.models.fields.IntegerField')(null=True, db_column=u'C105', blank=True)),
            ('school', self.gf('django.db.models.fields.IntegerField')(null=True, db_column=u'C106', blank=True)),
            ('household', self.gf('django.db.models.fields.IntegerField')(null=True, db_column=u'C107', blank=True)),
            ('unknown', self.gf('django.db.models.fields.IntegerField')(null=True, db_column=u'C108', blank=True)),
        ))
        db.send_create_signal('user', ['FocusPrice'])


    def backwards(self, orm):
        
        # Deleting model 'Profile'
        db.delete_table('user_profile')

        # Deleting model 'Zipcode'
        db.delete_table('user_zipcode')

        # Deleting model 'County'
        db.delete_table('user_county')

        # Deleting model 'FocusCountry'
        db.delete_table('user_focuscountry')

        # Deleting model 'FocusUser'
        db.delete_table(u'CustTurist_members')

        # Deleting model 'Actor'
        db.delete_table(u'Actor')

        # Deleting model 'ActorAddress'
        db.delete_table(u'ActAd')

        # Deleting model 'FocusZipcode'
        db.delete_table(u'PostalCode')

        # Deleting model 'FocusPrice'
        db.delete_table(u'Cust_Turist_Region_PriceCode_CrossTable')


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
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2012, 8, 1, 16, 59, 27, 263062)'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2012, 8, 1, 16, 59, 27, 262773)'}),
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
        'user.actor': {
            'Meta': {'object_name': 'Actor', 'db_table': "u'Actor'"},
            'accno': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_column': "u'AccNo'", 'blank': 'True'}),
            'actno': ('django.db.models.fields.IntegerField', [], {'db_column': "u'ActNo'"}),
            'actrel1': ('django.db.models.fields.IntegerField', [], {'db_column': "u'ActRel1'"}),
            'actrel2': ('django.db.models.fields.IntegerField', [], {'db_column': "u'ActRel2'"}),
            'actrel3': ('django.db.models.fields.IntegerField', [], {'db_column': "u'ActRel3'"}),
            'actrel4': ('django.db.models.fields.IntegerField', [], {'db_column': "u'ActRel4'"}),
            'actrel5': ('django.db.models.fields.IntegerField', [], {'db_column': "u'ActRel5'"}),
            'actrel6': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'db_column': "u'ActRel6'", 'blank': 'True'}),
            'actrel7': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'db_column': "u'ActRel7'", 'blank': 'True'}),
            'actrel8': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'db_column': "u'ActRel8'", 'blank': 'True'}),
            'actrel9': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'db_column': "u'ActRel9'", 'blank': 'True'}),
            'adtype': ('django.db.models.fields.CharField', [], {'max_length': '3', 'db_column': "u'AdType'", 'blank': 'True'}),
            'birth_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'db_column': "u'BDt'", 'blank': 'True'}),
            'chby': ('django.db.models.fields.CharField', [], {'max_length': '25', 'db_column': "u'ChBy'"}),
            'chdt': ('django.db.models.fields.DateTimeField', [], {'db_column': "u'ChDt'"}),
            'county1': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_column': "u'County1'", 'blank': 'True'}),
            'county2': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_column': "u'County2'", 'blank': 'True'}),
            'crby': ('django.db.models.fields.CharField', [], {'max_length': '25', 'db_column': "u'CrBy'"}),
            'crdt': ('django.db.models.fields.DateTimeField', [], {'db_column': "u'CrDt'"}),
            'disc': ('django.db.models.fields.SmallIntegerField', [], {'null': 'True', 'db_column': "u'Disc'", 'blank': 'True'}),
            'email': ('django.db.models.fields.CharField', [], {'max_length': '250', 'db_column': "u'EMail'", 'blank': 'True'}),
            'endcd': ('django.db.models.fields.CharField', [], {'max_length': '5', 'db_column': "u'EndCd'", 'blank': 'True'}),
            'enddt': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'db_column': "u'EndDt'", 'blank': 'True'}),
            'fax': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_column': "u'Fax'", 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_column': "u'FiNm'", 'blank': 'True'}),
            'inf1': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_column': "u'Inf1'", 'blank': 'True'}),
            'inf2': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_column': "u'Inf2'", 'blank': 'True'}),
            'inf3': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_column': "u'Inf3'", 'blank': 'True'}),
            'inf4': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_column': "u'Inf4'", 'blank': 'True'}),
            'inf5': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_column': "u'Inf5'", 'blank': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_column': "u'Nm'", 'blank': 'True'}),
            'mobph': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_column': "u'MobPh'", 'blank': 'True'}),
            'note1': ('django.db.models.fields.TextField', [], {'db_column': "u'Note1'", 'blank': 'True'}),
            'note2': ('django.db.models.fields.TextField', [], {'db_column': "u'Note2'", 'blank': 'True'}),
            'optbit1': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_column': "u'OptBit1'"}),
            'optbit2': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_column': "u'OptBit2'"}),
            'optbit3': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_column': "u'OptBit3'"}),
            'optbit4': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_column': "u'OptBit4'"}),
            'optbit5': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_column': "u'OptBit5'"}),
            'optbit6': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_column': "u'OptBit6'"}),
            'optchar1': ('django.db.models.fields.CharField', [], {'max_length': '10', 'db_column': "u'OptChar1'", 'blank': 'True'}),
            'optchar2': ('django.db.models.fields.CharField', [], {'max_length': '10', 'db_column': "u'OptChar2'", 'blank': 'True'}),
            'optchar3': ('django.db.models.fields.CharField', [], {'max_length': '10', 'db_column': "u'OptChar3'", 'blank': 'True'}),
            'optchar4': ('django.db.models.fields.CharField', [], {'max_length': '10', 'db_column': "u'OptChar4'", 'blank': 'True'}),
            'optchar5': ('django.db.models.fields.CharField', [], {'max_length': '10', 'db_column': "u'OptChar5'", 'blank': 'True'}),
            'optchar6': ('django.db.models.fields.CharField', [], {'max_length': '10', 'db_column': "u'OptChar6'", 'blank': 'True'}),
            'optchar7': ('django.db.models.fields.CharField', [], {'max_length': '10', 'db_column': "u'OptChar7'", 'blank': 'True'}),
            'optchar8': ('django.db.models.fields.CharField', [], {'max_length': '10', 'db_column': "u'OptChar8'", 'blank': 'True'}),
            'optchar9': ('django.db.models.fields.CharField', [], {'max_length': '10', 'db_column': "u'OptChar9'", 'blank': 'True'}),
            'optdate1': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'db_column': "u'OptDate1'", 'blank': 'True'}),
            'optdate2': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'db_column': "u'OptDate2'", 'blank': 'True'}),
            'optdate3': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'db_column': "u'OptDate3'", 'blank': 'True'}),
            'optdate4': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'db_column': "u'OptDate4'", 'blank': 'True'}),
            'optint1': ('django.db.models.fields.IntegerField', [], {'db_column': "u'OptInt1'"}),
            'optint2': ('django.db.models.fields.IntegerField', [], {'db_column': "u'OptInt2'"}),
            'optint3': ('django.db.models.fields.IntegerField', [], {'db_column': "u'OptInt3'"}),
            'optint4': ('django.db.models.fields.IntegerField', [], {'db_column': "u'OptInt4'"}),
            'optint5': ('django.db.models.fields.IntegerField', [], {'db_column': "u'OptInt5'"}),
            'optint6': ('django.db.models.fields.IntegerField', [], {'db_column': "u'OptInt6'"}),
            'optint7': ('django.db.models.fields.IntegerField', [], {'db_column': "u'OptInt7'"}),
            'optint8': ('django.db.models.fields.IntegerField', [], {'db_column': "u'OptInt8'"}),
            'optint9': ('django.db.models.fields.IntegerField', [], {'db_column': "u'OptInt9'"}),
            'optlng1': ('django.db.models.fields.FloatField', [], {'db_column': "u'OptLng1'"}),
            'optlng2': ('django.db.models.fields.FloatField', [], {'db_column': "u'OptLng2'"}),
            'optlng3': ('django.db.models.fields.FloatField', [], {'db_column': "u'OptLng3'"}),
            'orgno': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_column': "u'OrgNo'", 'blank': 'True'}),
            'payterm': ('django.db.models.fields.IntegerField', [], {'db_column': "u'PayTerm'"}),
            'ph': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_column': "u'Ph'", 'blank': 'True'}),
            'pno': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_column': "u'PNo'", 'blank': 'True'}),
            'seqno': ('django.db.models.fields.AutoField', [], {'primary_key': 'True', 'db_column': "u'SeqNo'"}),
            'sex': ('django.db.models.fields.CharField', [], {'max_length': '1', 'db_column': "u'Sex'", 'blank': 'True'}),
            'startcd': ('django.db.models.fields.CharField', [], {'max_length': '5', 'db_column': "u'StartCd'", 'blank': 'True'}),
            'startdt': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'db_column': "u'StartDt'", 'blank': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_column': "u'Type'"}),
            'vatcd': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_column': "u'VatCd'"}),
            'web': ('django.db.models.fields.CharField', [], {'max_length': '250', 'db_column': "u'Web'", 'blank': 'True'}),
            'webcrby': ('django.db.models.fields.CharField', [], {'max_length': '25', 'db_column': "u'WebCrBy'", 'blank': 'True'}),
            'webcrdt': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'db_column': "u'WebCrDt'", 'blank': 'True'}),
            'weblang': ('django.db.models.fields.CharField', [], {'max_length': '5', 'db_column': "u'WebLang'", 'blank': 'True'}),
            'webpw': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_column': "u'WebPw'", 'blank': 'True'}),
            'websh': ('django.db.models.fields.IntegerField', [], {'db_column': "u'WebSh'"}),
            'webusr': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_column': "u'WebUsr'", 'blank': 'True'})
        },
        'user.actoraddress': {
            'Meta': {'object_name': 'ActorAddress', 'db_table': "u'ActAd'"},
            'a1': ('django.db.models.fields.CharField', [], {'max_length': '40', 'db_column': "u'A1'", 'blank': 'True'}),
            'a2': ('django.db.models.fields.CharField', [], {'max_length': '40', 'db_column': "u'A2'", 'blank': 'True'}),
            'a3': ('django.db.models.fields.CharField', [], {'max_length': '40', 'db_column': "u'A3'", 'blank': 'True'}),
            'actadtype': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '3', 'db_column': "u'ActAdType'", 'blank': 'True'}),
            'actnojoin': ('django.db.models.fields.IntegerField', [], {'db_column': "u'ActNoJoin'"}),
            'actseqno': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['user.Actor']", 'unique': 'True', 'db_column': "u'ActSeqNo'"}),
            'chby': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_column': "u'ChBy'", 'blank': 'True'}),
            'chdt': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'db_column': "u'ChDt'", 'blank': 'True'}),
            'country': ('django.db.models.fields.CharField', [], {'max_length': '3', 'db_column': "u'CtryCode'", 'blank': 'True'}),
            'crby': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_column': "u'CrBy'", 'blank': 'True'}),
            'crdt': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'db_column': "u'CrDt'", 'blank': 'True'}),
            'frdt': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'db_column': "u'FrDt'", 'blank': 'True'}),
            'parea': ('django.db.models.fields.CharField', [], {'max_length': '30', 'db_column': "u'PArea'", 'blank': 'True'}),
            'seqno': ('django.db.models.fields.AutoField', [], {'primary_key': 'True', 'db_column': "u'SeqNo'"}),
            'todt': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'db_column': "u'ToDt'", 'blank': 'True'}),
            'zipcode': ('django.db.models.fields.CharField', [], {'max_length': '9', 'db_column': "u'PCode'", 'blank': 'True'})
        },
        'user.county': {
            'Meta': {'object_name': 'County'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'sherpa_id': ('django.db.models.fields.IntegerField', [], {'null': 'True'})
        },
        'user.focuscountry': {
            'Meta': {'object_name': 'FocusCountry'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'scandinavian': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'user.focusprice': {
            'Meta': {'object_name': 'FocusPrice', 'db_table': "u'Cust_Turist_Region_PriceCode_CrossTable'"},
            'association_id': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True', 'db_column': "u'Region'"}),
            'child': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'db_column': "u'C105'", 'blank': 'True'}),
            'household': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'db_column': "u'C107'", 'blank': 'True'}),
            'lifelong': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'db_column': "u'C104'", 'blank': 'True'}),
            'main': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'db_column': "u'C101'", 'blank': 'True'}),
            'school': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'db_column': "u'C106'", 'blank': 'True'}),
            'senior': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'db_column': "u'C103'", 'blank': 'True'}),
            'student': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'db_column': "u'C102'", 'blank': 'True'}),
            'unknown': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'db_column': "u'C108'", 'blank': 'True'})
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
        'user.focuszipcode': {
            'Meta': {'object_name': 'FocusZipcode', 'db_table': "u'PostalCode'"},
            'chby': ('django.db.models.fields.CharField', [], {'max_length': '25', 'db_column': "u'ChBy'", 'blank': 'True'}),
            'chdt': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'db_column': "u'ChDt'", 'blank': 'True'}),
            'county1name': ('django.db.models.fields.CharField', [], {'max_length': '40', 'db_column': "u'County1Name'", 'blank': 'True'}),
            'county1no': ('django.db.models.fields.CharField', [], {'max_length': '10', 'db_column': "u'County1No'", 'blank': 'True'}),
            'county2name': ('django.db.models.fields.CharField', [], {'max_length': '40', 'db_column': "u'County2Name'", 'blank': 'True'}),
            'county2no': ('django.db.models.fields.CharField', [], {'max_length': '10', 'db_column': "u'County2No'", 'blank': 'True'}),
            'crby': ('django.db.models.fields.CharField', [], {'max_length': '25', 'db_column': "u'CrBy'", 'blank': 'True'}),
            'crdt': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'db_column': "u'CrDt'", 'blank': 'True'}),
            'local_association_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'db_column': "u'District2'", 'blank': 'True'}),
            'main_association_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'db_column': "u'District1'", 'blank': 'True'}),
            'postarea': ('django.db.models.fields.CharField', [], {'max_length': '40', 'db_column': "u'PostArea'"}),
            'zipcode': ('django.db.models.fields.CharField', [], {'max_length': '9', 'primary_key': 'True', 'db_column': "u'PostCode'"})
        },
        'user.profile': {
            'Meta': {'object_name': 'Profile'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'password_restore_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'password_restore_key': ('django.db.models.fields.CharField', [], {'max_length': '40', 'unique': 'True', 'null': 'True'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.User']", 'unique': 'True'})
        },
        'user.zipcode': {
            'Meta': {'object_name': 'Zipcode'},
            'city': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'city_code': ('django.db.models.fields.CharField', [], {'max_length': '4'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'location': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'zipcode': ('django.db.models.fields.CharField', [], {'max_length': '4'})
        }
    }

    complete_apps = ['user']
