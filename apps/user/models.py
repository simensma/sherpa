from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.conf import settings
from django.core.cache import cache

from focus.models import Actor
from association.models import Association
from sherpa2.models import Association as Sherpa2Association

from itertools import groupby

class User(AbstractBaseUser):
    USERNAME_FIELD = 'identifier'

    # The identifier will be the memberid for members, and email address for
    # non-members.
    identifier = models.CharField(max_length=255, unique=True, db_index=True)

    # These three fields are only applicable for non-members; empty for members
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField()

    # DNT-employees can use this to separate home/work email addresses
    sherpa_email = models.EmailField()

    # Memberid is the link to Actor (membersystem user). Null for non-members
    memberid = models.IntegerField(null=True, unique=True)

    # Some users haven't registered but we still have some data relating to them
    # from various sources. They'll be created as inactive users, and registration
    # will if possible use the inactive user and retain the related data.
    is_active = models.BooleanField(default=True)

    # Password resets
    password_restore_key = models.CharField(max_length=settings.RESTORE_PASSWORD_KEY_LENGTH, null=True)
    password_restore_date = models.DateTimeField(null=True)

    # Used in the admin-interface for association-permissions
    associations = models.ManyToManyField('association.Association', related_name='+', through='AssociationRole')
    permissions = models.ManyToManyField('user.Permission', related_name='+')

    ### Methods ###

    def has_perm(self, perm):
        return self.permissions.filter(name=perm).exists()

    # Shortcut for templates to get any user perms via User
    def perms(self):
        return {p.name: True for p in self.permissions.all()}

    ### Focus-related ###

    def is_member(self):
        return self.memberid is not None

    # Return this users' Actor (cached), or None
    def get_actor(self):
        if not self.is_member():
            return None
        actor = cache.get('actor.%s' % self.memberid)
        if actor is None:
            actor = Actor.objects.get(memberid=self.memberid)
            cache.set('actor.%s' % self.memberid, actor, settings.FOCUS_MEMBER_CACHE_PERIOD)
        return actor

    def get_parent(self):
        if not self.is_household_member():
            return None

        parent_memberid = self.get_actor().get_parent_memberid()
        if parent_memberid is None:
            return None

        parent = cache.get('user.%s.parent' % self.memberid)
        if parent is None:
            try:
                parent = User.objects.get(memberid=parent_memberid)
            except User.DoesNotExist:
                parent = User(
                    identifier=parent_memberid,
                    memberid=parent_memberid,
                    is_active=False
                )
                parent.save()
                cache.set('user.%s.parent' % self.memberid, parent, settings.FOCUS_MEMBER_CACHE_PERIOD)
        return parent

    def get_children(self):
        children = cache.get('user.%s.children' % self.memberid)
        if children is None:
            children = []
            for actor_child in self.get_actor().get_children():
                try:
                    children.append(User.objects.get(memberid=actor_child.memberid))
                except User.DoesNotExist:
                    # Child without a User, create as inactive
                    child_user = User(
                        identifier=actor_child.memberid,
                        memberid=actor_child.memberid,
                        is_active=False
                    )
                    child_user.save()
                    children.append(child_user)
            cache.set('user.%s.children' % self.memberid, children, settings.FOCUS_MEMBER_CACHE_PERIOD)
        return children

    def is_household_member(self):
        return self.get_actor().is_household_member()

    def membership_type(self):
        return self.get_actor().membership_type()

    def has_membership_type(self, codename):
        # Note that you shouldn't use this to check for the 'household' membership type,
        # use is_household_member() -- see the docs in focus.Actor.is_household_member for more info.
        return self.get_actor().has_membership_type(codename)

    def get_first_name(self):
        if not self.is_member():
            return self.first_name
        else:
            return self.get_actor().first_name

    def get_last_name(self):
        if not self.is_member():
            return self.last_name
        else:
            return self.get_actor().last_name

    def get_full_name(self):
        if not self.is_member():
            return "%s %s" % (self.first_name, self.last_name)
        else:
            return self.get_actor().get_full_name()

    def get_email(self):
        if not self.is_member():
            return self.email
        else:
            return self.get_actor().get_email()

    def get_sherpa_email(self):
        if self.sherpa_email != '':
            return self.sherpa_email
        else:
            return self.get_email()

    def get_address(self):
        return self.get_actor().get_clean_address()

    def get_birth_date(self):
        return self.get_actor().birth_date

    def get_gender(self):
        return self.get_actor().get_gender()

    def get_age(self):
        return self.get_actor().get_age()

    def get_phone_home(self):
        return self.get_actor().get_phone_home()

    def get_phone_mobile(self):
        return self.get_actor().get_phone_mobile()

    def has_paid(self):
        return self.get_actor().has_paid()

    def is_eligible_for_publications(self):
        return self.get_actor().is_eligible_for_publications()

    def can_reserve_against_publications(self):
        return self.get_actor().can_reserve_against_publications()

    def get_reserved_against_fjellogvidde(self):
        return self.get_actor().get_reserved_against_fjellogvidde()

    def get_reserved_against_yearbook(self):
        return self.get_actor().get_reserved_against_yearbook()

    def has_foreign_fjellogvidde_service(self):
        return self.get_actor().has_foreign_fjellogvidde_service()

    def has_foreign_yearbook_service(self):
        return self.get_actor().has_foreign_yearbook_service()

    def get_invoice_type_text(self):
        return self.get_actor().get_invoice_type_text()

    def receive_email(self):
        return self.get_actor().receive_email

    def reserved_against_partneroffers(self):
        return self.get_actor().reserved_against_partneroffers

    def main_association(self):
        association = cache.get('user.association.%s' % self.get_actor().main_association_id)
        if association is None:
            association = Association.objects.get(focus_id=self.get_actor().main_association_id)
            cache.set('user.association.%s' % self.get_actor().main_association_id, association, 60 * 60 * 24 * 7)
        return association

    def main_association_old(self):
        # This sad method returns the association object from the old sherpa2 model.
        # For now it's mostly used to get the site url because most of the new objects
        # don't have an assigned site.
        association = cache.get('user.association_sherpa2.%s' % self.get_actor().main_association_id)
        if association is None:
            association = Sherpa2Association.objects.get(focus_id=self.get_actor().main_association_id)
            cache.set('user.association_sherpa2.%s' % self.get_actor().main_association_id, association, 60 * 60 * 24 * 7)
        return association

    # Returns associations this user has access to.
    # Note that this also takes permissions into account, e.g. sherpa admins will
    # have access to all associations
    def all_associations(self):
        associations = cache.get('user.%s.all_associations' % self.id)
        if associations is None:
            if self.has_perm('sherpa_admin'):
                # Sherpa admins have access to all associations
                associations = Association.objects.all()
                for association in associations:
                    association.role = 'admin'
            else:
                # A normal user, return all connected associations, including
                # children-associations where role is admin.
                associations = []
                for association in self.associations.all():
                    role = AssociationRole.objects.get(association=association, user=self).role
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
            cache.set('user.%s.all_associations' % self.id, associations, 60 * 60 * 24)
        return associations

    def all_associations_sorted(self):
        return Association.sort(self.all_associations())

    # Returns this users' associations, with all their children, regardless of role.
    # Used with aktiviteter where users can list their associations' children if desired
    # and set aktivitet-association to those too.
    def children_associations(self):
        associations = cache.get('user.%s.children_associations' % self.id)
        if associations is None:
            if self.has_perm('sherpa_admin'):
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
            cache.set('user.%s.children_associations' % self.id, associations, 60 * 60 * 24)
        return associations

    def children_associations_sorted(self):
        return Association.sort(self.children_associations())

    def is_eligible_for_norway_bus_tickets(self):
        if NorwayBusTicket.objects.filter(user=self).exists():
            # Only one order per member
            return False

        if self.norway_bus_tickets_offer_has_expired():
            # The offer applies only the same year as membership enrollment
            return False

        if not self.has_paid():
            # The offer applies only to active memberships
            return False

        return True

    def norway_bus_tickets_offer_has_expired(self):
        # Import here to avoid circular import
        from core.util import previous_membership_year_start
        return self.get_actor().start_date.date() < previous_membership_year_start()

    def show_norway_bus_tickets_menu_item(self):
        # Kind of complicated method, it's used in menus/navigation to show the link to
        # the order page - show it if the offer hasn't expired, but also if they have ordered before
        # even if it is expired.
        if not self.norway_bus_tickets_offer_has_expired():
            # Offer hasn't expired - show the item regardless of anything
            return True
        else:
            # Offer has expired - showing is only applicable if we HAVE made an order
            if NorwayBusTicket.objects.filter(user=self).exists():
                return True

            # No order, and offer expired - hide the item
            return False

    def merge_with(self, other_user):
        # This method transfers ALL objects related to the other user object
        # over to this one. ANY relation to the user object needs to be added here.
        # Typically, the merge occurs when a non-member registers their membership with a
        # memberid which exists for an imported inactive user. This is not often, but it
        # *can* happen. See the Sherpa docs for more info.
        # Whenever ForeignKeys to User are created, an entry needs to be created here
        # which transfers it. This is easy to miss, so be sure to search through the codebase
        # for missed tables from time to time. Use the 'userrelations' manage.py-command.

        from admin.models import Image
        from aktiviteter.models import AktivitetDate
        from articles.models import Article
        from fjelltreffen.models import Annonse
        from membership.models import SMSServiceRequest
        from page.models import Page, Variant, Version

        Annonse.objects.filter(user=other_user).update(user=self)
        Article.objects.filter(created_by=other_user).update(created_by=self)
        Article.objects.filter(modified_by=other_user).update(modified_by=self)
        AssociationRole.objects.filter(user=other_user).update(user=self)
        Image.objects.filter(uploader=other_user).update(uploader=self)
        NorwayBusTicket.objects.filter(user=other_user).update(user=self)
        Page.objects.filter(created_by=other_user).update(created_by=self)
        Page.objects.filter(modified_by=other_user).update(modified_by=self)
        SMSServiceRequest.objects.filter(user=other_user).update(user=self)
        Variant.objects.filter(owner=other_user).update(owner=self)
        Version.objects.filter(owner=other_user).update(owner=self)

        for version in Version.objects.filter(publishers=other_user):
            version.publishers.remove(other_user)
            version.publishers.add(self)
        for aktivitet_date in AktivitetDate.objects.filter(leaders=other_user):
            aktivitet_date.leaders.remove(other_user)
            aktivitet_date.leaders.add(self)
        for aktivitet_date in AktivitetDate.objects.filter(participants=other_user):
            aktivitet_date.participants.remove(other_user)
            aktivitet_date.participants.add(self)

        # Merge user-permissions.
        for p in other_user.permissions.all():
            self.permissions.add(p)

        # That should be everything. Since all objects should have been transferred, it's safe
        # to delete the other user. Note that if we forgot to transfer any objects, they
        # will be deleted.
        other_user.delete()

    @staticmethod
    def sherpa_users():
        permission = Permission.objects.get(name='sherpa')
        return User.objects.filter(permissions=permission, is_active=True)

class Permission(models.Model):
    # Django's Permission model is a bit more advanced than what we need,
    # so we'll roll our own.
    name = models.CharField(max_length=255)

class AssociationRole(models.Model):
    ROLE_CHOICES = (
        ('admin', 'Administrator'),
        ('user', 'Vanlig bruker'),)
    user = models.ForeignKey('user.User')
    association = models.ForeignKey('association.Association')
    role = models.CharField(max_length=255, choices=ROLE_CHOICES)

    @staticmethod
    def friendly_role(role):
        # Assumes that 'role' exists in the tuple and is unique
        return [c[1] for c in AssociationRole.ROLE_CHOICES if c[0] == role][0]

class NorwayBusTicket(models.Model):
    user = models.OneToOneField(User, related_name='norway_bus_ticket')
    date_placed = models.DateTimeField(auto_now_add=True)
    date_trip = models.DateTimeField(null=True) # Null for imported tickets
    # The imported trip dates have arbitrary text values which are hard to parse,
    # so store them separately in their original format.
    date_trip_text = models.CharField(max_length=25)
    distance = models.CharField(max_length=1024)
    is_imported = models.BooleanField(default=False)
