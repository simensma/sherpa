# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models

class Migration(DataMigration):

    depends_on = (
        ('admin', '0020_auto__add_field_image_new_uploader'),
        ('aktiviteter', '0019_auto'),
        ('articles', '0017_auto__add_field_article_new_created_by__add_field_article_new_modified'),
        ('fjelltreffen', '0015_auto__add_field_annonse_user'),
        ('membership', '0004_auto__add_field_smsservicerequest_user'),
        ('page', '0024_auto__add_field_version_new_owner__add_field_variant_new_owner__add_fi'),
    )

    def forwards(self, orm):
        # Create the new permission objects
        print("   Creating new permission objects...")
        sherpa_permission = orm['user.Permission'](name='sherpa')
        sherpa_permission.save()
        sherpa_admin_permission = orm['user.Permission'](name='sherpa_admin')
        sherpa_admin_permission.save()

        # Copy all user objects
        print("   Copying all users...")
        # Do me first, I should have ID 1! :)
        for old_user in orm['auth.User'].objects.filter(profile__memberid=3205691):
            old_profile = orm['user.Profile'].objects.get(user=old_user)
            new_user = orm['user.User']()

            # Identifier
            if old_profile.memberid is not None:
                # The identifier is still the memberid for members
                new_user.identifier = old_profile.memberid
            else:
                # For non-members, the identifier is now the actual email address, not a hash of it
                new_user.identifier = old_user.email

            # This should work, right? Just move over the hashed password. I haven't checked how
            # salt is set up etc.
            new_user.password = old_user.password

            new_user.first_name = old_user.first_name
            new_user.last_name = old_user.last_name
            new_user.email = old_user.email
            new_user.sherpa_email = old_profile.sherpa_email
            new_user.memberid = old_profile.memberid
            new_user.is_active = old_user.is_active
            new_user.password_restore_key = old_profile.password_restore_key
            new_user.password_restore_date = old_profile.password_restore_date
            new_user.save()

            # Permissions
            for p in old_user.user_permissions.all():
                if p.codename == 'sherpa':
                    new_user.permissions.add(sherpa_permission)
                elif p.codename == 'sherpa_admin':
                    new_user.permissions.add(sherpa_admin_permission)

        for old_user in orm['auth.User'].objects.exclude(profile__memberid=3205691):
            old_profile = orm['user.Profile'].objects.get(user=old_user)
            new_user = orm['user.User']()

            # Identifier
            if old_profile.memberid is not None:
                # The identifier is still the memberid for members
                new_user.identifier = old_profile.memberid
            else:
                # For non-members, the identifier is now the actual email address, not a hash of it
                new_user.identifier = old_user.email

            new_user.first_name = old_user.first_name
            new_user.last_name = old_user.last_name
            new_user.email = old_user.email
            new_user.sherpa_email = old_profile.sherpa_email
            new_user.memberid = old_profile.memberid
            new_user.is_active = old_user.is_active
            new_user.password_restore_key = old_profile.password_restore_key
            new_user.password_restore_date = old_profile.password_restore_date
            new_user.save()

            # Permissions
            for p in old_user.user_permissions.all():
                if p.codename == 'sherpa':
                    new_user.permissions.add(sherpa_permission)
                elif p.codename == 'sherpa_admin':
                    new_user.permissions.add(sherpa_admin_permission)

        print("   Updating images...")
        for image in orm['admin.Image'].objects.all():
            image.new_uploader = orm['user.User'].objects.get(memberid=image.uploader.memberid)
            image.save()

        print("   Updating aktiviteter...")
        for aktivitet_date in orm['aktiviteter.AktivitetDate'].objects.all():
            for leader in aktivitet_date.leaders.all():
                aktivitet_date.new_leaders.add(orm['user.User'].objects.get(memberid=leader.memberid))
            for participant in aktivitet_date.participants.all():
                aktivitet_date.new_participants.add(orm['user.User'].objects.get(memberid=participant.memberid))

        print("   Updating articles...")
        for article in orm['articles.Article'].objects.all():
            article.new_created_by = orm['user.User'].objects.get(memberid=article.created_by.memberid)
            if article.modified_by is not None:
                article.new_modified_by = orm['user.User'].objects.get(memberid=article.modified_by.memberid)
            else:
                article.new_modified_by = None
            article.save()

        print("   Updating fjelltreffenannonser...")
        for annonse in orm['fjelltreffen.Annonse'].objects.all():
            annonse.user = orm['user.User'].objects.get(memberid=annonse.profile.memberid)
            annonse.save()

        print("   Updating sms requests...")
        for sms in orm['membership.SMSServiceRequest'].objects.all():
            if sms.profile is not None:
                sms.user = orm['user.User'].objects.get(memberid=sms.profile.memberid)
            else:
                sms.user = None
            sms.save()

        print("   Updating cms-pages...")
        for page in orm['page.Page'].objects.all():
            page.new_created_by = orm['user.User'].objects.get(memberid=page.created_by.memberid)
            if page.modified_by is not None:
                page.new_modified_by = orm['user.User'].objects.get(memberid=page.modified_by.memberid)
            else:
                page.new_modified_by = None
            page.save()

        print("   Updating cms-variants...")
        for variant in orm['page.Variant'].objects.all():
            variant.new_owner = orm['user.User'].objects.get(memberid=variant.owner.memberid)
            variant.save()

        print("   Updating cms-versions...")
        for version in orm['page.Version'].objects.all():
            version.new_owner = orm['user.User'].objects.get(memberid=version.owner.memberid)
            version.save()
            for publisher in version.publishers.all():
                version.new_publishers.add(orm['user.User'].objects.get(memberid=publisher.memberid))

        print("   Updating associationroles...")
        for role in orm['user.AssociationRole'].objects.all():
            role.user = orm['user.User'].objects.get(memberid=role.profile.memberid)
            role.save()

        print("   Updating norway busticket-orders...")
        for ticket in orm['user.NorwayBusTicket'].objects.all():
            ticket.user = orm['user.User'].objects.get(memberid=ticket.profile.memberid)
            ticket.save()

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
            'new_uploader': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['user.User']", 'null': 'True'}),
            'photographer': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'tags': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'images'", 'symmetrical': 'False', 'to': u"orm['core.Tag']"}),
            'uploaded': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'uploader': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['user.Profile']"}),
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
            'leaders': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'leader_aktivitet_dates'", 'symmetrical': 'False', 'to': u"orm['user.Profile']"}),
            'new_leaders': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'new_leader_aktivitet_dates'", 'symmetrical': 'False', 'to': u"orm['user.User']"}),
            'new_participants': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'new_aktiviteter'", 'symmetrical': 'False', 'to': u"orm['user.User']"}),
            'participants': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'aktiviteter'", 'symmetrical': 'False', 'to': u"orm['user.Profile']"}),
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
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'articles_created'", 'to': u"orm['user.Profile']"}),
            'created_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'hide_thumbnail': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'articles_modified'", 'null': 'True', 'to': u"orm['user.Profile']"}),
            'modified_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'new_created_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'new_articles_created'", 'null': 'True', 'to': u"orm['user.User']"}),
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
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
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
            'profile': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'fjelltreffen_annonser'", 'to': u"orm['user.Profile']"}),
            'text': ('django.db.models.fields.TextField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'new_fjelltreffen_annonser'", 'null': 'True', 'to': u"orm['user.User']"})
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
            'profile': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['user.Profile']", 'null': 'True'}),
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
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'pages_created'", 'to': u"orm['user.Profile']"}),
            'created_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'pages_modified'", 'null': 'True', 'to': u"orm['user.Profile']"}),
            'modified_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'new_created_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'new_pages_created'", 'null': 'True', 'to': u"orm['user.User']"}),
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
            'new_owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'null': 'True', 'to': u"orm['user.User']"}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': u"orm['user.Profile']"}),
            'page': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['page.Page']", 'null': 'True'}),
            'priority': ('django.db.models.fields.IntegerField', [], {}),
            'segment': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['analytics.Segment']", 'null': 'True'})
        },
        u'page.version': {
            'Meta': {'object_name': 'Version'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'ads': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'new_owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'null': 'True', 'to': u"orm['user.User']"}),
            'new_publishers': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'new_versions'", 'symmetrical': 'False', 'to': u"orm['user.User']"}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': u"orm['user.Profile']"}),
            'publishers': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'versions'", 'symmetrical': 'False', 'to': u"orm['user.Profile']"}),
            'tags': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'versions'", 'symmetrical': 'False', 'to': u"orm['core.Tag']"}),
            'variant': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['page.Variant']"}),
            'version': ('django.db.models.fields.IntegerField', [], {})
        },
        u'user.associationrole': {
            'Meta': {'object_name': 'AssociationRole'},
            'association': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['association.Association']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'profile': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['user.Profile']"}),
            'role': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['user.User']", 'null': 'True'})
        },
        u'user.norwaybusticket': {
            'Meta': {'object_name': 'NorwayBusTicket'},
            'date_placed': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_trip': ('django.db.models.fields.DateTimeField', [], {}),
            'distance': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'profile': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'norway_bus_ticket'", 'unique': 'True', 'to': u"orm['user.Profile']"}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'new_norway_bus_ticket'", 'unique': 'True', 'null': 'True', 'to': u"orm['user.User']"})
        },
        u'user.norwaybusticketold': {
            'Meta': {'object_name': 'NorwayBusTicketOld'},
            'date_placed': ('django.db.models.fields.DateTimeField', [], {}),
            'date_trip_text': ('django.db.models.fields.CharField', [], {'max_length': '25'}),
            'distance': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'memberid': ('django.db.models.fields.IntegerField', [], {'unique': 'True'})
        },
        u'user.permission': {
            'Meta': {'object_name': 'Permission'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'user.profile': {
            'Meta': {'object_name': 'Profile'},
            'associations': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'users'", 'symmetrical': 'False', 'through': u"orm['user.AssociationRole']", 'to': u"orm['association.Association']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'memberid': ('django.db.models.fields.IntegerField', [], {'unique': 'True', 'null': 'True'}),
            'password_restore_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'password_restore_key': ('django.db.models.fields.CharField', [], {'max_length': '40', 'null': 'True'}),
            'sherpa_email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['auth.User']", 'unique': 'True'})
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
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'+'", 'symmetrical': 'False', 'to': u"orm['user.Permission']"}),
            'sherpa_email': ('django.db.models.fields.EmailField', [], {'max_length': '75'})
        }
    }

    complete_apps = ['admin', 'aktiviteter', 'articles', 'fjelltreffen', 'membership', 'page', 'user']
    symmetrical = True
