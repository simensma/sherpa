# -*- coding: utf-8 -*-
import datetime, os, re
from south.db import db
from south.v2 import DataMigration
from django.db import models

class Migration(DataMigration):

    def forwards(self, orm):
        def save_turleder(actor):
            try:
                user = orm['user.User'].objects.get(memberid=actor.memberid)
            except orm['user.User'].DoesNotExist:
                user = orm['user.User'](identifier=actor.memberid, memberid=actor.memberid, is_active=False)
                user.password = '!'
                user.save()

            dnt_oslo = orm['association.Association'].objects.get(name='DNT Oslo og Omegn')
            user.turleder_active_associations.add(dnt_oslo)

            if orm['user.Turleder'].objects.filter(user=user, role='vinter').exists():
                return

            today = datetime.date.today()

            # We can't just add 365*5 timedelta days because that doesn't account for leap years,
            # this does.
            try:
                five_years_from_now = datetime.date(year=(today.year + 5), month=today.month, day=today.day)
            except ValueError:
                # This will only occur when today is February 29th during a leap year (right?)
                five_years_from_now = datetime.date(year=(today.year + 5), month=today.month, day=(today.day-1))

            turleder = orm['user.Turleder'](
                user=user,
                role='vinter',
                association_approved=dnt_oslo,
                date_start=today,
                date_end=five_years_from_now
            )
            turleder.save() # This is what it's all about

        def parse_name(name):
            name = re.sub(',', '', name)
            name = name.strip()
            last_name, first_name = name.split(' ', 1)
            return first_name, last_name

        def zipcode(postal):
            return re.findall('\d{4}', postal)[0]

        with open('%s/0046_vinterturledere.txt' % os.path.dirname(__file__)) as f:
            lines = f.readlines()

        for line in lines:
            line = line.strip('\n').decode('iso-8859-1')
            name, address, postal, email, _, _, _, _, _, _, _ = line.split('\t')
            first_name, last_name = parse_name(name)
            address = address.strip()
            postal = postal.strip()
            email = email.strip()

            try:
                if email != '':
                    # Let's handle a couple special cases:
                    if email == 'sven.michaelis@web.de':
                        actor = orm['focus.Actor'].objects.get(email__iexact=email, first_name='Sven')
                    elif email == 'pettermjelva@gmail.com':
                        actor = orm['focus.Actor'].objects.get(email__iexact=email, first_name='Petter')
                    else:
                        actor = orm['focus.Actor'].objects.get(email__iexact=email)
                    save_turleder(actor)
                    continue
            except orm['focus.Actor'].DoesNotExist:
                pass

            try:
                actor = orm['focus.Actor'].objects.get(first_name__iexact=first_name, last_name__iexact=last_name)
                save_turleder(actor)
                continue
            except orm['focus.Actor'].DoesNotExist:
                pass
            except orm['focus.Actor'].MultipleObjectsReturned:
                try:
                    actor = orm['focus.Actor'].objects.get(first_name__iexact=first_name, last_name__iexact=last_name, address__zipcode=zipcode(postal))
                    save_turleder(actor)
                    continue
                except orm['focus.Actor'].DoesNotExist:
                    pass

            # Special cases:
            actor = None
            if first_name == 'Berg Arne' and last_name == 'Bakken':
                actor = orm['focus.Actor'].objects.get(memberid=1383264)
            elif first_name == 'Henrik WB' and last_name == 'Berger':
                actor = orm['focus.Actor'].objects.get(memberid=2447824)
            elif first_name == 'Nils' and last_name == 'Bloch-Hoell':
                actor = orm['focus.Actor'].objects.get(memberid=1079555)
            elif first_name == 'Gunnar' and last_name == 'Fermann':
                actor = orm['focus.Actor'].objects.get(memberid=2448181)
            elif first_name == 'Helge' and last_name == 'Fossberg':
                actor = orm['focus.Actor'].objects.get(memberid=1303590)
            elif first_name == 'Petter' and last_name == 'Kittelsen':
                actor = orm['focus.Actor'].objects.get(memberid=1480998)
            elif first_name == 'Knut (sv)' and last_name == 'Lykken':
                actor = orm['focus.Actor'].objects.get(memberid=1049231)
            elif first_name == 'Tor-Hermann' and last_name == u'Næss':
                actor = orm['focus.Actor'].objects.get(memberid=1065954)
            elif first_name == 'Hans Jacob' and last_name == 'Opsahl':
                actor = orm['focus.Actor'].objects.get(memberid=1239246)
            elif first_name == 'Mauritz' and last_name == 'Sendstad':
                actor = orm['focus.Actor'].objects.get(memberid=1168539)
            elif first_name == 'Chris' and last_name == 'Solheim-Allen':
                actor = orm['focus.Actor'].objects.get(memberid=1677152)
            elif first_name == 'Hugo Hvid' and last_name == u'Sørensen':
                actor = orm['focus.Actor'].objects.get(memberid=1180278)
            elif first_name == 'Jan Nordal' and last_name == u'Sørum':
                actor = orm['focus.Actor'].objects.get(memberid=1552286)
            elif first_name == 'Erik Bryn' and last_name == 'Tvedt':
                actor = orm['focus.Actor'].objects.get(memberid=1078988)

            if actor is not None:
                save_turleder(actor)
                continue

            # We'll note those few who pass here when running the migration, and return them to DNT Oslo.
            print("%s, %s#%s#%s#%s" % (last_name, first_name, address, postal, email))

    def backwards(self, orm):
        "Write your backwards methods here."

    models = {
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
        u'core.zipcode': {
            'Meta': {'object_name': 'Zipcode'},
            'area': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'city_code': ('django.db.models.fields.CharField', [], {'max_length': '4'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'zipcode': ('django.db.models.fields.CharField', [], {'max_length': '4'})
        },
        u'focus.actor': {
            'Meta': {'object_name': 'Actor', 'db_table': "u'Actor'"},
            'accno': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_column': "u'AccNo'"}),
            'actrel1': ('django.db.models.fields.IntegerField', [], {'db_column': "u'ActRel1'"}),
            'actrel2': ('django.db.models.fields.IntegerField', [], {'db_column': "u'ActRel2'"}),
            'actrel3': ('django.db.models.fields.IntegerField', [], {'db_column': "u'ActRel3'"}),
            'actrel7': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'db_column': "u'ActRel7'"}),
            'actrel8': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'db_column': "u'ActRel8'"}),
            'actrel9': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'db_column': "u'ActRel9'"}),
            'adtype': ('django.db.models.fields.CharField', [], {'max_length': '3', 'db_column': "u'AdType'"}),
            'birth_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'db_column': "u'BDt'"}),
            'chby': ('django.db.models.fields.CharField', [], {'max_length': '25', 'db_column': "u'ChBy'"}),
            'chdt': ('django.db.models.fields.DateTimeField', [], {'db_column': "u'ChDt'"}),
            'county1': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_column': "u'County1'"}),
            'county2': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_column': "u'County2'"}),
            'crby': ('django.db.models.fields.CharField', [], {'max_length': '25', 'db_column': "u'CrBy'"}),
            'crdt': ('django.db.models.fields.DateTimeField', [], {'db_column': "u'CrDt'"}),
            'disc': ('django.db.models.fields.SmallIntegerField', [], {'null': 'True', 'db_column': "u'Disc'"}),
            'email': ('django.db.models.fields.CharField', [], {'max_length': '250', 'db_column': "u'EMail'"}),
            'end_code': ('django.db.models.fields.CharField', [], {'max_length': '5', 'db_column': "u'EndCd'"}),
            'end_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'db_column': "u'EndDt'"}),
            'fax': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_column': "u'Fax'"}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_column': "u'FiNm'"}),
            'gender': ('django.db.models.fields.CharField', [], {'max_length': '1', 'db_column': "u'Sex'"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True', 'db_column': "u'SeqNo'"}),
            'inf1': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_column': "u'Inf1'"}),
            'inf2': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_column': "u'Inf2'"}),
            'inf3': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_column': "u'Inf3'"}),
            'inf4': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_column': "u'Inf4'"}),
            'inf5': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_column': "u'Inf5'"}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_column': "u'Nm'"}),
            'local_association_id': ('django.db.models.fields.IntegerField', [], {'db_column': "u'ActRel5'"}),
            'main_association_id': ('django.db.models.fields.IntegerField', [], {'db_column': "u'ActRel4'"}),
            'memberid': ('django.db.models.fields.IntegerField', [], {'unique': 'True', 'db_column': "u'ActNo'"}),
            'note1': ('django.db.models.fields.TextField', [], {'db_column': "u'Note1'"}),
            'note2': ('django.db.models.fields.TextField', [], {'db_column': "u'Note2'"}),
            'optbit2': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_column': "u'OptBit2'"}),
            'optbit4': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_column': "u'OptBit4'"}),
            'optbit5': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_column': "u'OptBit5'"}),
            'optbit6': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_column': "u'OptBit6'"}),
            'optchar1': ('django.db.models.fields.CharField', [], {'max_length': '10', 'db_column': "u'OptChar1'"}),
            'optchar2': ('django.db.models.fields.CharField', [], {'max_length': '10', 'db_column': "u'OptChar2'"}),
            'optchar3': ('django.db.models.fields.CharField', [], {'max_length': '10', 'db_column': "u'OptChar3'"}),
            'optchar4': ('django.db.models.fields.CharField', [], {'max_length': '10', 'db_column': "u'OptChar4'"}),
            'optchar5': ('django.db.models.fields.CharField', [], {'max_length': '10', 'db_column': "u'OptChar5'"}),
            'optchar6': ('django.db.models.fields.CharField', [], {'max_length': '10', 'db_column': "u'OptChar6'"}),
            'optchar7': ('django.db.models.fields.CharField', [], {'max_length': '10', 'db_column': "u'OptChar7'"}),
            'optchar8': ('django.db.models.fields.CharField', [], {'max_length': '10', 'db_column': "u'OptChar8'"}),
            'optchar9': ('django.db.models.fields.CharField', [], {'max_length': '10', 'db_column': "u'OptChar9'"}),
            'optdate1': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'db_column': "u'OptDate1'"}),
            'optdate2': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'db_column': "u'OptDate2'"}),
            'optdate3': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'db_column': "u'OptDate3'"}),
            'optdate4': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'db_column': "u'OptDate4'"}),
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
            'orgno': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_column': "u'OrgNo'"}),
            'parent': ('django.db.models.fields.IntegerField', [], {'db_column': "u'ActRel6'"}),
            'payterm': ('django.db.models.fields.IntegerField', [], {'db_column': "u'PayTerm'"}),
            'phone_home': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_column': "u'Ph'"}),
            'phone_mobile': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_column': "u'MobPh'"}),
            'pno': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_column': "u'PNo'"}),
            'receive_email': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_column': "u'OptBit1'"}),
            'reserved_against_partneroffers': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_column': "u'OptBit3'"}),
            'start_code': ('django.db.models.fields.CharField', [], {'max_length': '5', 'db_column': "u'StartCd'"}),
            'start_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'db_column': "u'StartDt'"}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_column': "u'Type'"}),
            'vatcd': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_column': "u'VatCd'"}),
            'web': ('django.db.models.fields.CharField', [], {'max_length': '250', 'db_column': "u'Web'"}),
            'webcrby': ('django.db.models.fields.CharField', [], {'max_length': '25', 'db_column': "u'WebCrBy'"}),
            'webcrdt': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'db_column': "u'WebCrDt'"}),
            'weblang': ('django.db.models.fields.CharField', [], {'max_length': '5', 'db_column': "u'WebLang'"}),
            'webpw': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_column': "u'WebPw'"}),
            'websh': ('django.db.models.fields.IntegerField', [], {'db_column': "u'WebSh'"}),
            'webusr': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_column': "u'WebUsr'"})
        },
        u'focus.actoraddress': {
            'Meta': {'object_name': 'ActorAddress', 'db_table': "u'ActAd'"},
            'a1': ('django.db.models.fields.CharField', [], {'max_length': '40', 'db_column': "u'A1'"}),
            'a2': ('django.db.models.fields.CharField', [], {'max_length': '40', 'db_column': "u'A2'"}),
            'a3': ('django.db.models.fields.CharField', [], {'max_length': '40', 'db_column': "u'A3'"}),
            'actadtype': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '3', 'db_column': "u'ActAdType'"}),
            'actnojoin': ('django.db.models.fields.IntegerField', [], {'db_column': "u'ActNoJoin'"}),
            'actor': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'address'", 'unique': 'True', 'db_column': "u'ActSeqNo'", 'to': u"orm['focus.Actor']"}),
            'area': ('django.db.models.fields.CharField', [], {'max_length': '30', 'db_column': "u'PArea'"}),
            'chby': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_column': "u'ChBy'"}),
            'chdt': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'db_column': "u'ChDt'"}),
            'country_code': ('django.db.models.fields.CharField', [], {'max_length': '3', 'db_column': "u'CtryCode'"}),
            'crby': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_column': "u'CrBy'"}),
            'crdt': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'db_column': "u'CrDt'"}),
            'frdt': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'db_column': "u'FrDt'"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True', 'db_column': "u'SeqNo'"}),
            'todt': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'db_column': "u'ToDt'"}),
            'zipcode': ('django.db.models.fields.CharField', [], {'max_length': '9', 'db_column': "u'PCode'"})
        },
        u'focus.actorservice': {
            'Meta': {'object_name': 'ActorService', 'db_table': "u'ActService'"},
            'actor': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'services'", 'db_column': "u'ActSeqNo'", 'to': u"orm['focus.Actor']"}),
            'actpayno': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'db_column': "u'ActPayNo'"}),
            'chby': ('django.db.models.fields.CharField', [], {'max_length': '25', 'db_column': "u'ChBy'"}),
            'chdt': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'db_column': "u'ChDt'"}),
            'code': ('django.db.models.fields.CharField', [], {'max_length': '25', 'db_column': "u'ArticleNo'"}),
            'crby': ('django.db.models.fields.CharField', [], {'max_length': '25', 'db_column': "u'CrBy'"}),
            'crdt': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'db_column': "u'CrDt'"}),
            'description': ('django.db.models.fields.TextField', [], {'db_column': "u'Description'"}),
            'end_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'db_column': "u'EndDt'"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True', 'db_column': "u'SeqNo'"}),
            'invdate': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'db_column': "u'InvDate'"}),
            'invoicefreq': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'db_column': "u'InvoiceFreq'"}),
            'invoicetype': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'db_column': "u'InvType'"}),
            'invprinttype': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'db_column': "u'InvPrintType'"}),
            'memberid': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'db_column': "u'ActNo'"}),
            'newstartdt': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'db_column': "u'NewStartDt'"}),
            'optint1': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'db_column': "u'OptInt1'"}),
            'previousinvoicedt': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'db_column': "u'PreviousInvoiceDt'"}),
            'price': ('django.db.models.fields.FloatField', [], {'null': 'True', 'db_column': "u'Price'"}),
            'pricecd': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'db_column': "u'PriceCd'"}),
            'qty': ('django.db.models.fields.FloatField', [], {'null': 'True', 'db_column': "u'Qty'"}),
            'start_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'db_column': "u'StartDt'"}),
            'stop_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'db_column': "u'StopDt'"})
        },
        u'focus.actortext': {
            'Meta': {'object_name': 'ActorText', 'db_table': "u'ActText'"},
            'actor': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'text'", 'unique': 'True', 'db_column': "u'ActSeqNo'", 'to': u"orm['focus.Actor']"}),
            'changed_by': ('django.db.models.fields.CharField', [], {'max_length': '25', 'db_column': "u'ChBy'"}),
            'changed_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'db_column': "u'ChDt'"}),
            'created_by': ('django.db.models.fields.CharField', [], {'max_length': '25', 'db_column': "u'CrBy'"}),
            'created_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'db_column': "u'CrDt'"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True', 'db_column': "u'SeqNo'"}),
            'memberid': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'db_column': "u'ActNo'"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_column': "u'TxtNm'"}),
            'text': ('django.db.models.fields.TextField', [], {'db_column': "u'Description'"}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_column': "u'TxtType'"})
        },
        u'focus.balancehistory': {
            'Meta': {'object_name': 'BalanceHistory', 'db_table': "u'Cust_Turist_Balance_Hist_v'"},
            'current_year': ('django.db.models.fields.FloatField', [], {'db_column': "u'ThisYear'"}),
            'id': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'balance'", 'unique': 'True', 'primary_key': 'True', 'db_column': "u'ActSeqNo'", 'to': u"orm['focus.Actor']"}),
            'memberid': ('django.db.models.fields.IntegerField', [], {'db_column': "u'ActActNo'"})
        },
        u'focus.enrollment': {
            'Meta': {'object_name': 'Enrollment', 'db_table': "u'CustTurist_members'"},
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
            'memberid': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True', 'db_column': "u'memberID'"}),
            'mob': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_column': "u'Mob'"}),
            'paid': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_column': "u'Payed'"}),
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
        u'focus.focuszipcode': {
            'Meta': {'object_name': 'FocusZipcode', 'db_table': "u'PostalCode'"},
            'area': ('django.db.models.fields.CharField', [], {'max_length': '40', 'db_column': "u'PostArea'"}),
            'chby': ('django.db.models.fields.CharField', [], {'max_length': '25', 'db_column': "u'ChBy'"}),
            'chdt': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'db_column': "u'ChDt'"}),
            'city_code': ('django.db.models.fields.CharField', [], {'max_length': '10', 'db_column': "u'County2No'"}),
            'city_name': ('django.db.models.fields.CharField', [], {'max_length': '40', 'db_column': "u'County2Name'"}),
            'county_code': ('django.db.models.fields.CharField', [], {'max_length': '10', 'db_column': "u'County1No'"}),
            'county_name': ('django.db.models.fields.CharField', [], {'max_length': '40', 'db_column': "u'County1Name'"}),
            'crby': ('django.db.models.fields.CharField', [], {'max_length': '25', 'db_column': "u'CrBy'"}),
            'crdt': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'db_column': "u'CrDt'"}),
            'local_association_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'db_column': "u'District2'"}),
            'main_association_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'db_column': "u'District1'"}),
            'zipcode': ('django.db.models.fields.CharField', [], {'max_length': '9', 'primary_key': 'True', 'db_column': "u'PostCode'"})
        },
        u'focus.price': {
            'Meta': {'object_name': 'Price', 'db_table': "u'Cust_Turist_Region_PriceCode_CrossTable'"},
            'association_id': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True', 'db_column': "u'Region'"}),
            'child': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'db_column': "u'C105'"}),
            'household': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'db_column': "u'C107'"}),
            'lifelong': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'db_column': "u'C104'"}),
            'main': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'db_column': "u'C101'"}),
            'school': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'db_column': "u'C106'"}),
            'senior': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'db_column': "u'C103'"}),
            'unknown': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'db_column': "u'C108'"}),
            'youth': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'db_column': "u'C102'"})
        },
        u'user.associationrole': {
            'Meta': {'object_name': 'AssociationRole'},
            'association': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['association.Association']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'role': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['user.User']"})
        },
        u'user.instruktor': {
            'Meta': {'object_name': 'Instruktor'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'role': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'instruktor'", 'to': u"orm['user.User']"})
        },
        u'user.kursleder': {
            'Meta': {'object_name': 'Kursleder'},
            'date_end': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'date_start': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'kursleder'", 'unique': 'True', 'to': u"orm['user.User']"})
        },
        u'user.norwaybusticket': {
            'Meta': {'object_name': 'NorwayBusTicket'},
            'date_placed': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_trip': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'date_trip_text': ('django.db.models.fields.CharField', [], {'max_length': '25'}),
            'distance': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_imported': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'norway_bus_ticket'", 'unique': 'True', 'to': u"orm['user.User']"})
        },
        u'user.permission': {
            'Meta': {'object_name': 'Permission'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'user.turleder': {
            'Meta': {'object_name': 'Turleder'},
            'association_approved': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'turledere_approved'", 'to': u"orm['association.Association']"}),
            'date_end': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'date_start': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'role': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'turledere'", 'to': u"orm['user.User']"})
        },
        u'user.user': {
            'Meta': {'object_name': 'User'},
            'associations': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'+'", 'symmetrical': 'False', 'through': u"orm['user.AssociationRole']", 'to': u"orm['association.Association']"}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'identifier': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255', 'db_index': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_expired': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'memberid': ('django.db.models.fields.IntegerField', [], {'unique': 'True', 'null': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'password_restore_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'password_restore_key': ('django.db.models.fields.CharField', [], {'max_length': '40', 'null': 'True'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'+'", 'symmetrical': 'False', 'to': u"orm['user.Permission']"}),
            'sherpa_email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'turleder_active_associations': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'active_turledere'", 'symmetrical': 'False', 'to': u"orm['association.Association']"})
        }
    }

    complete_apps = ['focus', 'association', 'user']
    symmetrical = True
