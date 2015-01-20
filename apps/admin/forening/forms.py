# encoding: utf-8
from django import forms

from foreninger.models import Forening
from foreninger.exceptions import ForeningTypeCannotHaveChildren, ForeningTypeNeedsParent, ForeningWithItselfAsParent, SentralForeningWithRelation, ForeningWithForeningParent, ForeningWithTurlagParent, TurlagWithTurgruppeParent, TurgruppeWithTurgruppeParent, ForeningParentIsChild, TurlagWithTurlagParent
from core.models import County, Zipcode
from user.models import User

class ForeningDataForm(forms.Form):
    def __init__(self, user, *args, **kwargs):
        super(ForeningDataForm, self).__init__(*args, **kwargs)
        self._user = user

        # If this is the create-form, and the user is not an admin, then they can only create turlag and turgrupper
        if type(self) == ForeningDataForm and not self._user.is_admin_in_dnt_central():
            self.fields['type'].choices = [t for t in Forening.TYPES if t[0] in ['turlag', 'turgruppe']]

    # Note that we're rendering parents manually, and not with the provided (or a custom) widget
    parents = forms.ModelMultipleChoiceField(
        required=False,
        queryset=Forening.objects.all(), # Not really the entire set, but that will be enforced in the model
    )

    name = forms.CharField(required=True, error_messages={
        'required': "Foreningen må ha et navn!",
    })

    name.widget.attrs.update({
        'class': 'form-control',
    })

    type = forms.ChoiceField(
        required=True,
        choices=Forening.TYPES, # May be overridden in __init__!
        error_messages={
            'required': "Du må velge hva slags forening dette er!",
        }
    )

    type.widget.attrs.update({
        'class': 'form-control',
        'data-chosen': '',
    })

    group_type = forms.ChoiceField(
        required=True,
        choices=Forening.GROUP_TYPES,
        error_messages={
            'required': "Du må velge hva slags turgruppe dette er!",
        }
    )

    group_type.widget.attrs.update({
        'class': 'form-control',
        'data-chosen': '',
    })

    post_address = forms.CharField(required=False)

    post_address.widget.attrs.update({
        'class': 'form-control'
    })

    visit_address = forms.CharField(required=False)

    visit_address.widget.attrs.update({
        'class': 'form-control'
    })

    zipcode = forms.CharField(required=False)

    counties = forms.ModelMultipleChoiceField(
        required=False,
        queryset=County.typical_objects().order_by('name')
    )

    counties.widget.attrs.update({
        'class': 'form-control',
        'data-chosen': '',
        'data-placeholder': 'Velg tilhørende fylke(r)...',
    })

    #
    # Contact information
    #

    choose_contact = forms.ChoiceField(
        required=True,
        widget=forms.RadioSelect(),
        choices=(
            ('forening', "Foreningen har egen kontaktinformasjon"),
            ('person', "En kontaktperson"),
        ),
        error_messages={
            'required': "Du må velge om det er foreningen eller en person som kan kontaktes",
        }
    )

    contact_person = forms.IntegerField(required=False, widget=forms.HiddenInput())

    contact_person_name = forms.CharField(required=False)

    contact_person_name.widget.attrs.update({
        'class': 'form-control',
    })

    phone = forms.CharField(required=False)

    phone.widget.attrs.update({
        'class': 'form-control',
    })

    email = forms.CharField(required=False)

    email.widget.attrs.update({
        'class': 'form-control',
    })

    organization_no = forms.CharField(required=False)

    organization_no.widget.attrs.update({
        'class': 'form-control',
    })

    gmap_url = forms.CharField(required=False, widget=forms.HiddenInput())

    facebook_url = forms.CharField(required=False)

    facebook_url.widget.attrs.update({
        'class': 'form-control',
    })

    def clean_name(self):
        return self.cleaned_data['name'].strip()

    def clean_post_address(self):
        return self.cleaned_data['post_address'].strip()

    def clean_visit_address(self):
        return self.cleaned_data['visit_address'].strip()

    def clean_zipcode(self):
        zipcode = self.cleaned_data['zipcode'].strip()
        if zipcode == '':
            return None
        try:
            zipcode = Zipcode.objects.get(zipcode=zipcode)
        except Zipcode.DoesNotExist:
            raise forms.ValidationError(
                "Postnummer %s er ikke registrert i postnummerregisteret!" % zipcode,
                code='invalid'
            )
        return zipcode

    def clean_contact_person(self):
        if self.cleaned_data['contact_person'] is None:
            return None
        else:
            return User.get_users().get(id=self.cleaned_data['contact_person'])

    def clean_contact_person_name(self):
        return self.cleaned_data['contact_person_name'].strip()

    def clean_phone(self):
        return self.cleaned_data['phone'].strip()

    def clean_email(self):
        return self.cleaned_data['email'].strip()

    def clean(self):
        cleaned_data = super(ForeningDataForm, self).clean()

        if cleaned_data.get('choose_contact') == 'person':
            if cleaned_data.get('contact_person') is None and \
                (cleaned_data.get('contact_person_name') is None or cleaned_data.get('contact_person_name') == ''):
                self.add_error(
                    'contact_person_name',
                    u"Hvis det er en kontaktperson som kan kontaktes, må du oppgi et navn eller velge en person " \
                    u"fra medlemsregisteret.",
                )

        type_ = cleaned_data.get('type')
        parents = cleaned_data.get('parents')

        if type_ in ['sentral', 'forening']:
            # In this case, the UI will have hidden the parents input, but it might still have a value, so
            # force it to empty. The hiding of the field should make this behavior intuitive.
            cleaned_data['parent'] = []
            parents = []

        # These types must have a parent, but that can't be enforced on the DB-level for *new* foreninger since parents
        # are a M2M-relationship (so the child needs to be saved before the parent can be related), so check it here.
        elif type_ in ['turlag', 'turgruppe'] and len(parents) == 0:
            self.add_error(
                'parents',
                u"%s må ha en moderforening!" % (
                    'Et turlag' if type_ == 'turlag' else 'En turgruppe',
                )
            )
            parents = None

        # Non DNT admins cannot *create* forening with type forening/sentral
        # Note that this might be legal in derived classes, so check this only for the base class
        # Shouldn't be possible without a manual POST
        if type(self) == ForeningDataForm and not self._user.is_admin_in_dnt_central() and type_ in ['sentral', 'forening']:
            self.add_error(
                'type',
                u"Du har ikke tillatelse til å opprette sentrale grupper eller medlemsforeninger. Vennligst ta " \
                u"kontakt med DNT sentralt.",
            )

        # Validate the new forening type and parents relationship
        try:
            forening = Forening()
            forening.validate_relationships(
                simulate_type=type_,
                simulate_parents=parents,
            )

        except ForeningWithItselfAsParent:
            # Shouldn't be possible without a manual POST
            self.add_error(
                'parents',
                u"%s kan ikke være underlagt seg selv." % forening.name
            )

        except SentralForeningWithRelation:
            # Shouldn't be possible without a manual POST
            self.add_error(
                'parents',
                u"En sentral forening kan ikke ha noen koblinger til andre foreningstyper."
            )

        except ForeningWithForeningParent:
            self.add_error(
                'parents',
                u"En forening kan ikke være underlagt en annen forening."
            )

        except TurlagWithTurlagParent:
            self.add_error(
                'parents',
                u"Et turlag kan ikke være underlagt et annet turlag."
            )

        except TurgruppeWithTurgruppeParent:
            self.add_error(
                'parents',
                u"En turgruppe kan ikke være underlagt en annen turgruppe."
            )

        except ForeningWithTurlagParent:
            self.add_error(
                'parents',
                u"Foreninger kan ikke være underlagt turlag/turgrupper."
            )

        except TurlagWithTurgruppeParent:
            self.add_error(
                'parents',
                u"Et turlag kan ikke være underlagt en turgruppe."
            )

class ExistingForeningDataForm(ForeningDataForm):

    forening = forms.IntegerField(required=False, widget=forms.HiddenInput())

    def clean_forening(self):
        return Forening.objects.get(id=self.cleaned_data['forening'])

    def clean(self):
        cleaned_data = super(ExistingForeningDataForm, self).clean() or self.cleaned_data

        forening = cleaned_data.get('forening')
        parents = cleaned_data.get('parents')
        new_type = cleaned_data.get('type')

        # If the previous form threw some errors, let those propagate without our derived logic cluttering
        # Ideally, we should carefully check each case and provide as many errors as possible, but can't
        # spend time on that right now
        if not 'forening' in cleaned_data or not 'parents' in cleaned_data or not 'type' in cleaned_data:
            return

        # Non DNT admins cannot *change* the type to forening/sentral
        if not self._user.is_admin_in_dnt_central():
            # Cannot change an existing sentral/forening at all
            if forening.type in ['sentral', 'forening'] and forening.type != new_type:
                self.add_error(
                    'type',
                    u"Du har ikke tillatelse til å endre gruppetypen for %s - vennligst ta kontakt med DNT " \
                    u"sentralt." % forening.name
                )

            # Cannot change turlag/turgruppe to sentral/forening
            elif forening.type in ['turlag', 'turgruppe'] and new_type in ['sentral', 'forening']:
                self.add_error(
                    'type',
                    u"Du har ikke tillatelse til å endre gruppetypen for %s til denne typen forening - vennligst " \
                    u"ta kontakt med DNT sentralt." % forening.name
                )

        # This validation was performed in our base class for a new forening, but recheck for the chosen existing
        # forening. We only need to catch the relevant new types; this forening may have children, and it
        # may have the parent as a child - the rest would've been catched in our base check.
        try:
            forening.validate_relationships(
                simulate_type=new_type,
                simulate_parents=parents,
            )

        except ForeningTypeNeedsParent:
            # This will never happen as long as our base class performs this check explicitly for us, and we're
            # skipping these validations when our base class has errors. However, this is where it would belong
            # if one of those conditions ever change.
            self.add_error(
                'parent',
                u"%s må ha en moderforening!" % (
                    'Et turlag' if new_type == 'turlag' else 'En turgruppe',
                ),
            )

        except ForeningTypeCannotHaveChildren:
            self.add_error(
                'type',
                u"Hvis du vil gjøre %s til %s, kan den ikke ha noen underforeninger. (Gruppen har %s " \
                u"underforeninger i dag)" % (
                    forening.name, new_type, forening.children.count(),
                ),
            )

        except ForeningParentIsChild as e:
            self.add_error(
                'parents',
                u"%s er allerede en undergruppe av %s. Da kan ikke %s være underlagt %s samtidig." % (
                    e.parent.name, forening.name, forening.name, e.parent.name,
                ),
            )
