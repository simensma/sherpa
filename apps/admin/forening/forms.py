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
        if type(self) == ForeningDataForm and not self._user.is_admin_in_main_central():
            self.fields['type'].choices = [t for t in Forening.TYPES if t[0] in ['turlag', 'turgruppe']]

    # Note that we're rendering parent manually, and not with the provided (or a custom) widget
    parent = forms.ModelChoiceField(
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

    gmap_url = forms.CharField(required=False)

    gmap_url.widget.attrs.update({
        'class': 'form-control',
    })

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

        type_ = cleaned_data.get('type')
        parent = cleaned_data.get('parent')

        if type_ in ['sentral', 'forening']:
            # In this case, the UI will have hidden the parent input, but it might still have a value, so
            # force it to None. The hiding of the field should make this behavior intuitive.
            cleaned_data['parent'] = None
            parent = None

        # Non DNT admins cannot *create* forening with type forening/sentral
        # Note that this might be legal in derived classes, so check this only for the base class
        # Shouldn't be possible without a manual POST
        if type(self) == ForeningDataForm and not self._user.is_admin_in_main_central() and type_ in ['sentral', 'forening']:
            self._errors['type'] = self.error_class([
                u"Du har ikke tillatelse til å opprette sentrale grupper eller medlemsforeninger. Vennligst ta kontakt med DNT sentralt."
            ])
            if 'type' in cleaned_data:
                del cleaned_data['type']

        # Validate the new forening type and parent relationship
        try:
            forening = Forening(
                parent=parent,
                type=type_,
            )

            forening.validate_relationships()

        except ForeningTypeNeedsParent:
            self._errors['parent'] = self.error_class([
                u"%s må ha en moderforening!" % (
                    'Et turlag' if type_ == 'turlag' else 'En turgruppe',
                )
            ])
            if 'parent' in cleaned_data:
                del cleaned_data['parent']

        except ForeningWithItselfAsParent:
            # Shouldn't be possible without a manual POST
            self._errors['parent'] = self.error_class([
                u"%s kan ikke være underlagt seg selv." % forening.name
            ])
            if 'parent' in cleaned_data:
                del cleaned_data['parent']

        except SentralForeningWithRelation:
            # Shouldn't be possible without a manual POST
            self._errors['parent'] = self.error_class([
                u"En sentral forening kan ikke ha noen koblinger til andre foreningstyper."
            ])
            if 'parent' in cleaned_data:
                del cleaned_data['parent']

        except ForeningWithForeningParent:
            self._errors['parent'] = self.error_class([
                u"En forening kan ikke være underlagt en annen forening."
            ])
            if 'parent' in cleaned_data:
                del cleaned_data['parent']

        except TurlagWithTurlagParent:
            self._errors['parent'] = self.error_class([
                u"Et turlag kan ikke være underlagt et annet turlag."
            ])
            if 'parent' in cleaned_data:
                del cleaned_data['parent']

        except TurgruppeWithTurgruppeParent:
            self._errors['parent'] = self.error_class([
                u"En turgruppe kan ikke være underlagt en annen turgruppe."
            ])
            if 'parent' in cleaned_data:
                del cleaned_data['parent']

        except ForeningWithTurlagParent:
            self._errors['parent'] = self.error_class([
                u"Foreninger kan ikke være underlagt turlag/turgrupper."
            ])
            if 'parent' in cleaned_data:
                del cleaned_data['parent']

        except TurlagWithTurgruppeParent:
            self._errors['parent'] = self.error_class([
                u"Et turlag kan ikke være underlagt en turgruppe."
            ])
            if 'parent' in cleaned_data:
                del cleaned_data['parent']

        return cleaned_data

class ExistingForeningDataForm(ForeningDataForm):

    forening = forms.IntegerField(required=False, widget=forms.HiddenInput())

    def clean_forening(self):
        return Forening.objects.get(id=self.cleaned_data['forening'])

    def clean(self):
        cleaned_data = super(ExistingForeningDataForm, self).clean()

        forening = cleaned_data.get('forening')
        parent = cleaned_data.get('parent')
        new_type = cleaned_data.get('type')

        # If the previous form threw some errors, let those propagate without our derived logic cluttering
        # Ideally, we should carefully check each case and provide as many errors as possible, but can't
        # spend time on that right now
        if not 'forening' in cleaned_data or not 'parent' in cleaned_data or not 'type' in cleaned_data:
            return cleaned_data

        # Non DNT admins cannot *change* the type to forening/sentral
        if not self._user.is_admin_in_main_central():
            # Cannot change an existing sentral/forening at all
            if forening.type in ['sentral', 'forening'] and forening.type != new_type:
                self._errors['type'] = self.error_class([
                    u"Du har ikke tillatelse til å endre gruppetypen for %s - vennligst ta kontakt med DNT sentralt." % (
                        forening.name,
                    )
                ])
                if 'type' in cleaned_data:
                    del cleaned_data['type']

            # Cannot change turlag/turgruppe to sentral/forening
            elif forening.type in ['turlag', 'turgruppe'] and new_type in ['sentral', 'forening']:
                self._errors['type'] = self.error_class([
                    u"Du har ikke tillatelse til å endre gruppetypen for %s til denne typen forening - vennligst ta kontakt med DNT sentralt." % (
                        forening.name,
                    )
                ])
                if 'type' in cleaned_data:
                    del cleaned_data['type']

        # This validation was performed in our parent for a new forening, but recheck for the chosen existing
        # forening. We only need to catch the relevant new types; this forening may have children, and it
        # may have the parent as a child - the rest would've been catched in our base check.
        try:
            original_type = forening.type
            original_parent = forening.parent
            forening.type = new_type
            forening.parent = parent

            forening.validate_relationships()

        except ForeningTypeCannotHaveChildren:
            self._errors['type'] = self.error_class([
                u"Hvis du vil gjøre %s til %s, kan den ikke ha noen underforeninger. (Gruppen har %s underforeninger i dag)" % (
                    forening.name,
                    new_type,
                    forening.children.count(),
                )
            ])
            del cleaned_data['type']

        except ForeningParentIsChild:
            self._errors['parent'] = self.error_class([
                u"%s er allerede en undergruppe av %s. Da kan ikke %s være underlagt %s samtidig." % (
                    parent.name, forening.name, forening.name, parent.name
                )
            ])
            del cleaned_data['parent']

        finally:
            # Reset the original forening objects' data - we're not supposed to change that here
            forening.type = original_type
            forening.parent = original_parent

        return cleaned_data
