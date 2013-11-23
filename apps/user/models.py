# encoding: utf-8
from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.conf import settings
from django.core.cache import cache
from django.utils import crypto

from focus.models import Actor, Enrollment
from association.models import Association, dnt_oslo_id, dnt_ung_oslo_id
from sherpa2.models import Association as Sherpa2Association, dnt_oslo_id as dnt_oslo_id_sherpa2, dnt_ung_oslo_id as dnt_ung_oslo_id_sherpa2
from focus.abstractions import ActorProxy

from itertools import groupby
from datetime import date
import json

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
    is_inactive = models.BooleanField(default=False)

    # Actors can be deleted from Focus for various reasons. Whenever discovered,
    # we'll set this to True to mark them as expired.
    is_expired = models.BooleanField(default=False)

    # After enrollment, the Actor won't exist until the enrollment is validated by
    # medlemsservice, but in order to give the new member a preliminary User we'll
    # create a pending one which uses 'focus.models.Enrollment'.
    is_pending = models.BooleanField(default=False)
    pending_registration_key = models.CharField(max_length=settings.RESTORE_PASSWORD_KEY_LENGTH, null=True)

    # Password resets
    password_restore_key = models.CharField(max_length=settings.RESTORE_PASSWORD_KEY_LENGTH, null=True)
    password_restore_date = models.DateTimeField(null=True)

    # Used in the admin-interface for association-permissions
    associations = models.ManyToManyField('association.Association', related_name='+', through='AssociationRole')
    permissions = models.ManyToManyField('user.Permission', related_name='+')

    # If turleder, where this turleder is active. The user.Turleder model defines certificates.
    # It's possible, but not correct, that this field has references when there are none in user.Turleder.
    turleder_active_associations = models.ManyToManyField('association.Association', related_name='active_turledere')


    #
    # Turleder-stuff
    #

    def get_highest_turleder_role(self):
        return Turleder.sort_by_role(self.turledere.all())[0]

    def get_instruktor_roles(self):
        current_roles = [i.role for i in self.instruktor.all()]
        return [{
            'key': role['key'],
            'name': role['name'],
            'active': role['key'] in current_roles
        } for role in Instruktor.ROLE_CHOICES]

    def get_active_instruktor_roles(self):
        return [r for r in self.get_instruktor_roles() if r['active']]

    #
    # Membership/Focus
    #

    def is_member(self):
        return self.memberid is not None

    def should_be_expired(self):
        """
        Regardless of is_expired is set or not, check if this user should be expired.
        """
        return not self.is_pending and not Actor.objects.filter(memberid=self.memberid).exists()

    def get_actor(self):
        """
        Return this users' Actor (cached), or an ActorProxy if this is a pending user
        """
        if not self.is_member():
            raise Exception("You cannot call get_actor() on a non-member, check your code logic")

        try:
            if self.is_pending:
                return ActorProxy(self.memberid)
            else:
                actor = cache.get('actor.%s' % self.memberid)
                if actor is None:
                    actor = Actor.objects.get(memberid=self.memberid)
                    cache.set('actor.%s' % self.memberid, actor, settings.FOCUS_MEMBER_CACHE_PERIOD)
                return actor
        except (Enrollment.DoesNotExist, Actor.DoesNotExist) as e:
            # Seems this user is expired. Since this could be called from anywhere, we can't give a
            # proper error message, we'll just have to re-raise the exception. But we can at least
            # set is_expired to True, so it hopefully doesn't happen again with this user.
            self.is_expired = True
            self.save()
            raise e

    def get_parent(self):
        if not self.is_pending and not self.is_household_member():
            return None

        parent_memberid = self.get_actor().get_parent_memberid()
        if parent_memberid is None:
            return None

        parent = cache.get('user.%s.parent' % self.memberid)
        if parent is None:
            parent = User.get_or_create_inactive(memberid=parent_memberid)
            cache.set('user.%s.parent' % self.memberid, parent, settings.FOCUS_MEMBER_CACHE_PERIOD)
        return parent

    def get_children(self):
        children = cache.get('user.%s.children' % self.memberid)
        if children is None:
            children = []
            for actor_child in self.get_actor().get_children():
                children.append(User.get_or_create_inactive(memberid=actor_child.memberid))
            cache.set('user.%s.children' % self.memberid, children, settings.FOCUS_MEMBER_CACHE_PERIOD)
        return children

    def get_membership_start_date(self):
        return self.get_actor().start_date.date()

    def is_household_member(self):
        return self.get_actor().is_household_member()

    def membership_type(self):
        return self.get_actor().membership_type()

    def has_membership_type(self, codename):
        """
        Note that you shouldn't use this to check for the 'household' membership type,
        use is_household_member() -- see the docs in focus.Actor.is_household_member for more info.
        """
        return self.get_actor().has_membership_type(codename)

    #
    # Specific to pending users - checks focus.models.Enrollment
    #

    def verify_still_pending(self, ignore_cache=False):
        # Cache the check for an hour
        if not ignore_cache and cache.get('user.%s.checked_for_pending' % self.memberid) is not None:
            return True
        cache.set('user.%s.checked_for_pending' % self.memberid, True, 60 * 60)

        if Actor.objects.filter(memberid=self.memberid).exists():
            self.is_pending = False
            self.save()
            return False
        else:
            return True

    def get_payment_method_text(self):
        if not self.is_pending:
            raise Exception("Can't check payment method for non-pending users, check your logic.")

        return self.get_actor().get_payment_method_text()

    def get_enrollment_registration_date(self):
        if not self.is_pending:
            raise Exception("Can't check enrollment registration for non-pending users, check your logic.")

        return self.get_actor().get_enrollment_registration_date()

    #
    # Personalia and Focus queries
    #

    def get_first_name(self):
        if not self.is_member():
            return self.first_name
        else:
            return self.get_actor().get_first_name()

    def get_last_name(self):
        if not self.is_member():
            return self.last_name
        else:
            return self.get_actor().get_last_name()

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

    def set_email(self, email):
        if not self.is_member():
            self.email = email
            self.save()
        else:
            self.get_actor().set_email(email)

    def get_sherpa_email(self):
        if self.sherpa_email != '':
            return self.sherpa_email
        else:
            return self.get_email()

    def get_address(self):
        return self.get_actor().get_clean_address()

    def get_birth_date(self):
        return self.get_actor().get_birth_date()

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

    def get_payment_years(self):
        from core.util import membership_year_start
        start_date = membership_year_start()['actual_date']
        today = date.today()
        years = {
            'current': today.year,
            'next': today.year + 1
        }
        if today >= start_date:
            if self.get_actor().has_paid_next_year():
                years['code'] = 'both'
                return years
            elif self.get_actor().has_paid_this_year():
                years['code'] = 'current_not_next'
                return years
            else:
                years['code'] = 'neither_years'
                return years
        else:
            if self.get_actor().has_paid_this_year():
                years['code'] = 'current'
                return years
            else:
                years['code'] = 'not_this_year'
                return years

    def is_eligible_for_publications(self):
        return self.get_actor().is_eligible_for_publications()

    def can_reserve_against_publications(self):
        return self.get_actor().can_reserve_against_publications()

    def get_reserved_against_fjellogvidde(self):
        return self.get_actor().get_reserved_against_fjellogvidde()

    def set_reserved_against_fjellogvidde(self, reserved):
        self.get_actor().set_reserved_against_fjellogvidde(reserved)

    def get_reserved_against_yearbook(self):
        return self.get_actor().get_reserved_against_yearbook()

    def set_reserved_against_yearbook(self, reserved):
        self.get_actor().set_reserved_against_yearbook(reserved)

    def has_foreign_fjellogvidde_service(self):
        return self.get_actor().has_foreign_fjellogvidde_service()

    def has_foreign_yearbook_service(self):
        return self.get_actor().has_foreign_yearbook_service()

    def get_invoice_type_text(self):
        return self.get_actor().get_invoice_type_text()

    def receive_email(self):
        return self.get_actor().receive_email

    def set_receive_email(self, receive):
        actor = self.get_actor()
        actor.receive_email = receive
        actor.save()

    def reserved_against_partneroffers(self):
        return self.get_actor().reserved_against_partneroffers

    def set_reserved_against_partneroffers(self, reserved):
        actor = self.get_actor()
        actor.reserved_against_partneroffers = reserved
        actor.save()

    def main_association(self):
        association = cache.get('user.%s.association' % self.identifier)
        if association is None:
            association = Association.objects.get(focus_id=self.get_actor().main_association_id)

            # Well, here's an interesting special case. We want youth members of DNT Oslo og Omegn
            # to actually be a member of DNT ung Oslo og Omegn, but our member system can't handle that,
            # so we'll have to check for that and change it here. Note that this applies only to Oslo
            # and no other member associations.
            if association.id == dnt_oslo_id and self.membership_type()['codename'] == 'youth':
                association = Association.objects.get(id=dnt_ung_oslo_id)

            cache.set('user.%s.association' % self.identifier, association, 60 * 60 * 24)
        return association

    def main_association_old(self):
        """
        This sad method returns the association object from the old sherpa2 model.
        For now it's mostly used to get the site url because most of the new objects
        don't have an assigned site. Cache heavily since this hits the old DB.
        """

        # Users' association cache
        association = cache.get('user.%s.association_sherpa2' % self.identifier)
        if association is None:

            # The actual association cache
            association = cache.get('association_sherpa2.focus.%s' % self.get_actor().main_association_id)
            if association is None:
                association = Sherpa2Association.objects.get(focus_id=self.get_actor().main_association_id)
                cache.set('association_sherpa2.focus.%s' % focus_association_id, association, 60 * 60 * 24 * 7)

            # Special case, just like in main_association()
            if association.id == dnt_oslo_id_sherpa2 and self.membership_type()['codename'] == 'youth':
                # Get the DNT ung Oslo association, use the association cache
                association = cache.get('association_sherpa2.%s' % dnt_ung_oslo_id_sherpa2)
                if association is None:
                    association = Sherpa2Association.objects.get(id=dnt_ung_oslo_id_sherpa2)
                    cache.set('association_sherpa2.%s' % dnt_ung_oslo_id_sherpa2, association, 60 * 60 * 24 * 7)

            cache.set('user.%s.association_sherpa2' % self.identifier, association, 60 * 60 * 24 * 7)
        return association

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
        from core.util import membership_year_start
        last_year = date.today().year - 1
        return self.get_membership_start_date() < membership_year_start(year=last_year)['public_date']

    def show_norway_bus_tickets_menu_item(self):
        """
        Kind of complicated method, it's used in menus/navigation to show the link to
        the order page - show it if the offer hasn't expired, but also if they have ordered before
        even if it is expired.
        """
        if not self.norway_bus_tickets_offer_has_expired():
            # Offer hasn't expired - show the item regardless of anything
            return True
        else:
            # Offer has expired - showing is only applicable if we HAVE made an order
            if NorwayBusTicket.objects.filter(user=self).exists():
                return True

            # No order, and offer expired - hide the item
            return False

    def update_personal_data(self, attributes, address_attributes=None):
        """
        Setter for updating personal data in Focus. Doesn't have a concept of accepted attributes, so they are
        kind of 'leaked out' to the callers (e.g. the field name for address.a1). Maybe it *should* have that
        at some point.
        """

        actor = self.get_actor()

        for name, value in attributes.items():
            actor.__setattr__(name, value)
        actor.save()

        if address_attributes is not None:
            for name, value in address_attributes.items():
                actor.address.__setattr__(name, value)
            actor.address.save()

    #
    # Permissions and association permissions, for Sherpa users
    #

    def has_perm(self, perm):
        return self.permissions.filter(name=perm).exists()

    def perms(self):
        """
        Shortcut for templates to get any user perms via User
        """
        return {p.name: True for p in self.permissions.all()}

    def can_modify_user_memberid(self):
        """
        Users who have access to DNT's central association can modify memberids
        in Sherpa.
        """
        # It's okay to look this up by name, right?
        dnt_central = Association.objects.get(name='Den Norske Turistforening')
        return dnt_central in self.all_associations()

    def can_modify_kursleder_status(self):
        """
        Users who have access to DNT's central association can assign kursleder-status
        """
        dnt_central = Association.objects.get(name='Den Norske Turistforening')
        return dnt_central in self.all_associations()

    def all_associations(self):
        """
        Returns associations this user has access to.
        Note that this also takes permissions into account, e.g. sherpa admins will
        have access to all associations
        """
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

    def children_associations(self):
        """
        Returns this users' associations, with all their children, regardless of role.
        Used with aktiviteter where users can list their associations' children if desired
        and set aktivitet-association to those too.
        """
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

    def merge_with(self, other_user, move_password=False):
        """
        This method transfers ALL objects related to the other user object
        over to this one. This occurs:
        - When a non-member registers their membership with a memberid which already exists
          for an inactive user
        - When someone decides to change a users' memberid to another, which already has another
          user
        See the Sherpa docs for more info.

        Whenever relations to User are created, an entry needs to be created here
        which transfers it. This is easy to miss, so be sure to search through the codebase
        for missed tables from time to time. Use the 'userrelations' manage.py-command.
        """

        from admin.models import Image
        from aktiviteter.models import AktivitetDate
        from articles.models import Article
        from fjelltreffen.models import Annonse
        from membership.models import SMSServiceRequest
        from page.models import Page, Variant, Version
        from user.models import Turleder

        # Ordered alphabetically (and so is 'userrelations')

        # aktiviteter.AktivitetDate:
        for aktivitet_date in AktivitetDate.objects.filter(turledere=other_user):
            aktivitet_date.turledere.remove(other_user)
            aktivitet_date.turledere.add(self)
        for aktivitet_date in AktivitetDate.objects.filter(participants=other_user):
            aktivitet_date.participants.remove(other_user)
            aktivitet_date.participants.add(self)

        # fjelltreffen.Annonse:
        Annonse.objects.filter(user=other_user).update(user=self)

        # articles.Article:
        Article.objects.filter(created_by=other_user).update(created_by=self)
        Article.objects.filter(modified_by=other_user).update(modified_by=self)

        # user.AssociationRole:
        AssociationRole.objects.filter(user=other_user).update(user=self)

        # admin.Image:
        Image.objects.filter(uploader=other_user).update(uploader=self)

        # user.NorwayBusTicket:
        # Note that this is a OneToOneField.
        try:
            old_ticket = NorwayBusTicket.objects.get(user=other_user)
        except NorwayBusTicket.DoesNotExist:
            old_ticket = None

        try:
            new_ticket = self.norway_bus_ticket
        except NorwayBusTicket.DoesNotExist:
            new_ticket = None

        if old_ticket is not None and new_ticket is not None:
            # Well, both users have a ticket. Not sure which we want, it kind of depends on the
            # context of which the merge was called. Let's just keep the newest one for now.
            # This might need to be reviewed later.
            pass
        elif old_ticket is not None:
            old_ticket.user = self
            old_ticket.save()

        # user.Turleder:
        Turleder.objects.filter(user=other_user).update(user=self)

        # page.Page:
        Page.objects.filter(created_by=other_user).update(created_by=self)
        Page.objects.filter(modified_by=other_user).update(modified_by=self)

        # membership.SMSServiceRequest:
        SMSServiceRequest.objects.filter(user=other_user).update(user=self)

        # user.User:
        # The 'associations' relation is already handled through AssociationRole
        self.permissions = other_user.permissions.all()

        # page.Variant:
        Variant.objects.filter(owner=other_user).update(owner=self)

        # page.Version:
        Version.objects.filter(owner=other_user).update(owner=self)
        for version in Version.objects.filter(publishers=other_user):
            version.publishers.remove(other_user)
            version.publishers.add(self)

        # Move the hashed password
        if move_password:
            self.password = other_user.password

        # That should be everything. Since all objects should have been transferred, it's safe
        # to delete the other user. Note that if we forgot to transfer any objects, they
        # will be deleted.
        self.save()
        other_user.delete()

    #
    # Static methods
    #

    @staticmethod
    def get_users(include_pending=False):
        """
        Filter on what we consider the 'current' userbase, i.e. not expired users.
        Typically this shouldn't include pending users (until they're accepted), but
        in some rare cases we *do* want them too, hence the include_pending parameter.
        """
        users = User.objects.filter(is_expired=False)
        if not include_pending:
            users = users.exclude(is_pending=True)
        return users

    @staticmethod
    def sherpa_users():
        permission = Permission.objects.get(name='sherpa')
        return User.get_users().filter(permissions=permission, is_inactive=False)

    @staticmethod
    def get_or_create_inactive(memberid):
        try:
            return User.get_users().get(memberid=memberid)
        except User.DoesNotExist:
            return User.create_inactive_user(memberid)

    @staticmethod
    def create_inactive_user(memberid):
        Actor.objects.get(memberid=memberid) # Verify that the Actor exists
        try:
            # Check if the user already exists first.
            existing_user = User.objects.get(memberid=memberid)

            # Note that we don't check if this user is inactive or not.
            # If they are, maybe someone double-clicked some link or something.
            # It doesn't matter, let this user pass as the created one.

            if existing_user.is_pending:
                # Well, we saw that they're not pending anymore since we checked the
                # actor, so fix that and let them pass.
                existing_user.is_pending = False
                existing_user.save()

            if existing_user.is_expired:
                # Oh, what happened here? Well, they're not expired anymore since we
                # the actor exists, so fix that and let them pass.
                existing_user.is_expired = False
                existing_user.save()

            return existing_user
        except User.DoesNotExist:
            user = User(identifier=memberid, memberid=memberid, is_inactive=True)
            user.set_unusable_password()
            user.save()
            return user

    @staticmethod
    def create_pending(memberid):
        Enrollment.get_active().get(memberid=memberid) # Ensure that the enrollment exists
        user = User(
            identifier='%s' % memberid,
            memberid=memberid,
            is_inactive=True,
            is_pending=True
        )
        user.set_unusable_password()
        key = crypto.get_random_string(length=settings.RESTORE_PASSWORD_KEY_LENGTH)
        while User.objects.filter(pending_registration_key=key).exists():
            # Ensure that the key isn't already in use. With the current key length of 40, we'll have
            # ~238 bits of entropy which means that this will never ever happen, ever.
            # You will win the lottery before this happens. And I want to know if it does, so log it.
            logger.warning(u"Noen fikk en random-generert pending-registration-key som allerede finnes!",
                exc_info=sys.exc_info(),
                extra={
                    'request': request,
                    'should_you_play_the_lottery': True,
                    'key': key
                }
            )
            key = crypto.get_random_string(length=settings.RESTORE_PASSWORD_KEY_LENGTH)
        user.pending_registration_key = key
        user.save()
        return user

class Permission(models.Model):
    """
    Django's Permission model is a bit more advanced than what we need,
    so we'll roll our own.
    """
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

class Turleder(models.Model):
    TURLEDER_CHOICES = (
        (u'vinter', u'Vinterturleder'),
        (u'sommer', u'Sommerturleder'),
        (u'grunnleggende', u'Grunnleggende turleder'),
        (u'ambassadør', u'DNT Ambassadør'),)
    user = models.ForeignKey(User, related_name='turledere')
    role = models.CharField(max_length=255, choices=TURLEDER_CHOICES)
    association_approved = models.ForeignKey('association.Association', related_name='turledere_approved')
    date_start = models.DateField(null=True)
    date_end = models.DateField(null=True)

    def get_role(self):
        return [c[1] for c in self.TURLEDER_CHOICES if c[0] == self.role][0]

    def is_expired(self):
        return self.date_end <= date.today()

    @staticmethod
    def sort_by_role(roles):
        order = {i[0]: Turleder.TURLEDER_CHOICES.index(i) for i in Turleder.TURLEDER_CHOICES}
        return sorted(roles, key=lambda t: order[t.role])

class Kursleder(models.Model):
    user = models.OneToOneField(User, related_name='kursleder')
    date_start = models.DateField(null=True)
    date_end = models.DateField(null=True)

    def is_expired(self):
        return self.date_end <= date.today()

class Instruktor(models.Model):
    # Instruktør-roles - like turleder, but a bit more casual
    ROLE_CHOICES = [
        {'key': u'klatre', 'name': u'Klatreinstruktør'},
        {'key': u'klatre_inne', 'name': u'Klatreinstruktør inne'},
        {'key': u'klatre_sport', 'name': u'Klatreinstruktør sport'},
        {'key': u'fjellkurs_leder', 'name': u'Fjellkursleder'},
        {'key': u'bre', 'name': u'Breinstruktør'},
        {'key': u'padle', 'name': u'Padleinstruktør'},
        {'key': u'skred', 'name': u'Skredinstruktør'},
        {'key': u'telemark', 'name': u'Telemarkinstruktør'},
        {'key': u'snowboard', 'name': u'Snowboardinstruktør'},
        {'key': u'senior', 'name': u'Seniorturleder'},
        {'key': u'ungdom', 'name': u'Ungdomsturleder'},
        {'key': u'barn', 'name': u'Barnas turleder'},
        {'key': u'politi', 'name': u'Godkjent politiattest'},
    ]

    user = models.ForeignKey(User, related_name='instruktor')
    role = models.CharField(max_length=255)
