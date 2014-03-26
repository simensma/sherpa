# encoding: utf-8
from django import forms

from foreninger.models import Forening
from core.models import County, Zipcode

class ForeningDataForm(forms.Form):

    parent = forms.ModelChoiceField(
        required=False,
        queryset=Forening.objects.exclude(type='sentral').order_by('name'),
        empty_label='',
    )

    parent.widget.attrs.update({
        'class': 'form-control chosen',
        'data-placeholder': 'Velg moderforening...',
    })

    name = forms.CharField(required=True, error_messages={
        'required': "Foreningen må ha et navn!",
    })

    name.widget.attrs.update({
        'class': 'form-control',
    })

    type = forms.ChoiceField(
        required=True,
        choices=Forening.TYPES,
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

    zipcode = forms.CharField(required=False) # Let clean_zipcode() handle missing zipcode too

    counties = forms.ModelMultipleChoiceField(
        required=False,
        queryset=County.typical_objects().order_by('name')
    )

    counties.widget.attrs.update({
        'class': 'form-control',
        'data-chosen': '',
        'data-placeholder': 'Velg tilhørende fylke(r)...',
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
        try:
            zipcode = Zipcode.objects.get(zipcode=zipcode)
        except Zipcode.DoesNotExist:
            raise forms.ValidationError(
                "Postnummer %s er ikke registrert i postnummerregisteret!" % zipcode,
                code='invalid'
            )
        return zipcode

class ExistingForeningDataForm(ForeningDataForm):
    def __init__(self, *args, **kwargs):
        """Exclude the current forening from the parent-choices"""
        super(ExistingForeningDataForm, self).__init__(*args, **kwargs)
        if 'forening' in self.initial:
            self.fields['parent'].queryset = self.fields['parent'].queryset.exclude(id=self.initial['forening'])

    forening = forms.IntegerField(required=False, widget=forms.HiddenInput())

    def clean_forening(self):
        return Forening.objects.get(id=self.cleaned_data['forening'])

    def clean(self):
        cleaned_data = super(ExistingForeningDataForm, self).clean()

        forening = cleaned_data.get('forening')
        parent = cleaned_data.get('parent')

        #
        # Relationship rules between forening/parent based on type
        #

        if parent is None:
            # No parent defined

            if forening.type in ['turlag', 'turgruppe']:
                # These types need a parent
                self._errors['parent'] = self.error_class([
                    u"%s må ha en moderforening!" % (
                        'Et turlag' if forening.type == 'turlag' else 'En turgruppe',
                    )
                ])
                del cleaned_data['parent']

        else:
            # A parent defined, validate child/parent rules

            if forening == parent:
                # An object can't be child of itself
                # Shouldn't be possible without a manual POST, we're excluding this forening from the parent choices
                self._errors['parent'] = self.error_class([
                    u"%s kan ikke være underlagt seg selv." % forening.name
                ])
                del cleaned_data['parent']

            elif forening.type == 'sentral' or parent.type == 'sentral':
                # Central can't have relationships
                # Shouldn't be possible without a manual POST
                self._errors['parent'] = self.error_class([
                    u"En sentral forening kan ikke ha noen koblinger til andre foreningstyper."
                ])
                del cleaned_data['parent']

            elif forening.type == 'forening' and parent.type == 'forening':
                # Forening can't be child of other forening
                self._errors['parent'] = self.error_class([
                    u"En forening kan ikke være underlagt en annen forening."
                ])
                del cleaned_data['parent']

            elif forening.type == 'forening' and parent.type in ['turlag', 'turgruppe']:
                # Forening can't be child of turlag/turgruppe
                self._errors['parent'] = self.error_class([
                    u"Foreninger kan ikke være underlagt turlag/turgrupper."
                ])
                del cleaned_data['parent']

            elif forening.type == 'turlag' and parent.type == 'turgruppe':
                # Turlag can't be child of turgruppe
                self._errors['parent'] = self.error_class([
                    u"Et turlag kan ikke være underlagt en turgruppe."
                ])
                del cleaned_data['parent']

            elif parent in forening.get_children_deep():
                # Parent shouldn't already be a children of its new child
                self._errors['parent'] = self.error_class([
                    u"%s er allerede en undergruppe av %s. Da kan ikke %s være underlagt %s samtidig." % (
                        parent.name, forening.name, forening.name, parent.name
                    )
                ])
                del cleaned_data['parent']

        return self.cleaned_data
