# encoding: utf-8
from django import forms

from foreninger.models import Forening
from core.models import County, Zipcode

class ForeningDataForm(forms.Form):

    parent = forms.ModelChoiceField(
        required=False,
        queryset=Forening.objects.order_by('name'),
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

        if forening == parent:
            # Shouldn't be possible, we're excluding this forening from the parent choices
            self._errors['parent'] = self.error_class([
                "%s er allerede en underforening av %s. Da kan du ikke sette %s under %s." % (
                    parent.name, forening.name, forening.name, parent.name
                )
            ])
            del cleaned_data['parent']

        elif parent in forening.get_children_deep():
            self._errors['parent'] = self.error_class([
                "%s er allerede en underforening av %s. Da kan du ikke sette %s under %s." % (
                    parent.name, forening.name, forening.name, parent.name
                )
            ])
            del cleaned_data['parent']

        return self.cleaned_data
