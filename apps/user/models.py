from django.db import models
from django.contrib.auth.models import User, Permission
from django.conf import settings
from django.core.cache import cache
from django.contrib.auth.context_processors import PermWrapper

from focus.models import Actor
from association.models import Association

from itertools import groupby
from datetime import datetime

class Profile(models.Model):
    user = models.OneToOneField(User)
    password_restore_key = models.CharField(max_length=settings.RESTORE_PASSWORD_KEY_LENGTH, null=True)
    password_restore_date = models.DateTimeField(null=True)
    associations = models.ManyToManyField('association.Association', related_name='users', through='AssociationRole')
    memberid = models.IntegerField(null=True, unique=True)
    sherpa_email = models.EmailField()

    # Shortcut for templates to get any user perms via Profile
    def perms(self):
        return PermWrapper(self.user)

    ### Focus-related ###

    # Return this users' Actor (cached), or None
    def get_actor(self):
        if not self.is_member():
            return None
        actor = cache.get('actor.%s' % self.memberid)
        if actor is None:
            actor = Actor.objects.get(memberid=self.memberid)
            cache.set('actor.%s' % self.memberid, actor, settings.FOCUS_MEMBER_CACHE_PERIOD)
        return actor

    def is_member(self):
        return self.memberid is not None

    def get_first_name(self):
        if not self.is_member():
            return self.user.first_name
        else:
            return self.get_actor().first_name

    def get_last_name(self):
        if not self.is_member():
            return self.user.last_name
        else:
            return self.get_actor().last_name

    def get_full_name(self):
        if not self.is_member():
            return self.user.get_full_name()
        else:
            return "%s %s" % (self.get_actor().first_name, self.get_actor().last_name)

    def get_email(self):
        if not self.is_member():
            return self.user.email
        else:
            return self.get_actor().email

    def get_sherpa_email(self):
        if self.sherpa_email != '':
            return self.sherpa_email
        else:
            return self.get_email()

    # Returns associations this user has access to.
    # Note that this also takes permissions into account, e.g. sherpa admins will
    # have access to all associations
    def all_associations(self):
        associations = cache.get('profile.%s.all_associations' % self.id)
        if associations is None:
            if self.user.has_perm('user.sherpa_admin'):
                # Sherpa admins have access to all associations
                associations = Association.objects.all()
                for association in associations:
                    association.role = 'admin'
            else:
                # A normal user, return all connected associations, including
                # children-associations where role is admin.
                associations = []
                for association in self.associations.all():
                    role = AssociationRole.objects.get(association=association, profile=self).role
                    if role == 'admin':
                        # Add this one and all its children
                        for association in association.get_with_children():
                            association.role = 'admin'
                            associations.append(association)
                    elif role == 'user':
                        # Just add this one
                        association.role = 'user'
                        associations.append(association)

                # Since this will add duplicates if any of the related associations
                # are child/parent-related with each other, remove the one with lowest role
                def pick_dupe(associations):
                    # This defines role priority
                    # Pick the dupe with role admin if existing, if not, just pick any dupe.
                    admins = [a for a in associations if a.role == 'admin']
                    if len(admins) > 0:
                        return admins[0]
                    else:
                        return associations[0]

                ## Sort and group by association id, and remove dupes
                sorted_associations = sorted(associations, key=lambda a: a.id)
                grouped_associations = groupby(sorted_associations, key=lambda a: a.id)
                associations = [pick_dupe(list(group)) for key, group in grouped_associations]
            cache.set('profile.%s.all_associations' % self.id, associations, 60 * 60 * 24)
        return associations

    def all_associations_sorted(self):
        return Association.sort(self.all_associations())

    # Returns this users' associations, with all their children, regardless of role.
    # Used with aktiviteter where users can list their associations' children if desired
    # and set aktivitet-association to those too.
    def children_associations(self):
        associations = cache.get('profile.%s.children_associations' % self.id)
        if associations is None:
            if self.user.has_perm('user.sherpa_admin'):
                # Sherpa admins have access to all associations
                associations = Association.objects.all()
                #for association in associations:
                #    association.role = 'admin'
            else:
                # A normal user, return all connected associations with their children
                associations = []
                for association in self.associations.all():
                    for association in association.get_with_children():
                        # association.role = 'admin'
                        associations.append(association)

                # Since this will add duplicates if any of the related associations
                # are child/parent-related with each other, sort and group by association
                # id and remove dupes.
                sorted_associations = sorted(associations, key=lambda a: a.id)
                grouped_associations = groupby(sorted_associations, key=lambda a: a.id)
                associations = [list(group)[0] for key, group in grouped_associations]
            cache.set('profile.%s.children_associations' % self.id, associations, 60 * 60 * 24)
        return associations

    def children_associations_sorted(self):
        return Association.sort(self.children_associations())

    def is_eligible_for_norway_bus_tickets(self):
        if NorwayBusTicket.objects.filter(profile=self).exists():
            # Only one order per member
            return False

        if NorwayBusTicketOld.objects.filter(memberid=self.memberid).exists():
            # Old, imported order. Still only one order per member
            return False

        if self.norway_bus_tickets_offer_has_expired():
            # The offer applies only the same year as membership enrollment
            return False

        if not self.get_actor().has_paid():
            # The offer applies only to active memberships
            return False

        return True

    def norway_bus_tickets_offer_has_expired(self):
        return self.get_actor().start_date.year < datetime.now().year

    def show_norway_bus_tickets_menu_item(self):
        # Kind of complicated method, it's used in menus/navigation to show the link to
        # the order page - show it if the offer hasn't expired, but also if they have ordered before
        # even if it is expired.
        if not self.norway_bus_tickets_offer_has_expired():
            # Offer hasn't expired - show the item regardless of anything
            return True
        else:
            # Offer has expired - showing is only applicable if we HAVE made an order
            if NorwayBusTicket.objects.filter(profile=self).exists():
                return True

            if NorwayBusTicketOld.objects.filter(memberid=self.memberid).exists():
                return True

            # No orders, and offer expired - hide the item
            return False

    def merge_with(self, other_profile):
        # This method transfers ALL objects related to the other profile object
        # over to this one. ANY relation to the profile object needs to be added here.
        # Typically, the merge occurs when a non-member registers their membership with a
        # memberid which exists for an imported inactive user. This is not often, but it
        # *can* happen. See the Sherpa docs for more info.
        # Whenever ForeignKeys to Profile are created, an entry needs to be created here
        # which transfers it. This is easy to miss, so be sure to search through the codebase
        # for missed tables from time to time. Use the 'profilerelations' manage.py-command.

        from admin.models import Image
        from aktiviteter.models import AktivitetDate
        from articles.models import Article
        from fjelltreffen.models import Annonse
        from membership.models import SMSServiceRequest
        from page.models import Page, Variant, Version

        Annonse.objects.filter(profile=other_profile).update(profile=self)
        Article.objects.filter(created_by=other_profile).update(created_by=self)
        Article.objects.filter(modified_by=other_profile).update(modified_by=self)
        AssociationRole.objects.filter(profile=other_profile).update(profile=self)
        Image.objects.filter(uploader=other_profile).update(uploader=self)
        NorwayBusTicket.objects.filter(profile=other_profile).update(profile=self)
        Page.objects.filter(created_by=other_profile).update(created_by=self)
        Page.objects.filter(modified_by=other_profile).update(modified_by=self)
        SMSServiceRequest.objects.filter(profile=other_profile).update(profile=self)
        Variant.objects.filter(owner=other_profile).update(owner=self)
        Version.objects.filter(owner=other_profile).update(owner=self)

        for version in Version.objects.filter(publishers=other_profile):
            version.publishers.remove(other_profile)
            version.publishers.add(self)
        for aktivitet_date in AktivitetDate.objects.filter(leaders=other_profile):
            aktivitet_date.leaders.remove(other_profile)
            aktivitet_date.leaders.add(self)
        for aktivitet_date in AktivitetDate.objects.filter(participants=other_profile):
            aktivitet_date.participants.remove(other_profile)
            aktivitet_date.participants.add(self)

        # Merge user-permissions.
        for p in other_profile.user.user_permissions.all():
            self.user.user_permissions.add(p)

        # That should be everything. Since all objects should have been transferred, it's safe
        # to delete the other profile. Note that if we forgot to transfer any objects, they
        # will be deleted.
        other_profile.user.delete()
        other_profile.delete()

    @staticmethod
    def sherpa_users():
        permission = Permission.objects.get(codename='sherpa')
        return Profile.objects.filter(user__user_permissions=permission)

    class Meta:
        permissions = [
            ("sherpa_admin", "Sherpa-administrator - global access"),
            ("sherpa", "Has general access to Sherpa"),
        ]

class AssociationRole(models.Model):
    ROLE_CHOICES = (
        ('admin', 'Administrator'),
        ('user', 'Vanlig bruker'),)
    profile = models.ForeignKey('user.Profile')
    association = models.ForeignKey('association.Association')
    role = models.CharField(max_length=255, choices=ROLE_CHOICES)

    @staticmethod
    def friendly_role(role):
        # Assumes that 'role' exists in the tuple and is unique
        return [c[1] for c in AssociationRole.ROLE_CHOICES if c[0] == role][0]

class NorwayBusTicket(models.Model):
    profile = models.OneToOneField(Profile, related_name='norway_bus_ticket')
    date_placed = models.DateTimeField(auto_now_add=True)
    date_trip = models.DateTimeField()
    distance = models.CharField(max_length=1024)

# This model contains a bunch of imported orders from the old user system.
# During the new user page launch year (probably 2013), we need this to know who have already
# ordered in order to deny further orders. However, at the end of that year, this could in theory
# be deleted (because members can only order new tickets the same year as enrollment),
# but it's kept because we use it to show users who have already ordered information about
# their order.
class NorwayBusTicketOld(models.Model):
    # Note that memberid cannot be a foreign key reference to Profile, as not all members
    # who've placed orders have created their user profile here at the time of import.
    memberid = models.IntegerField(unique=True)
    date_placed = models.DateTimeField()
    # The imported trip dates have arbitrary text values which are hard to parse,
    # so we'll skip that for now.
    date_trip_text = models.CharField(max_length=25)
    distance = models.CharField(max_length=255)
