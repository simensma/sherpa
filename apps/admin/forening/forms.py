# encoding: utf-8
from django import forms

from core.models import County, Zipcode

class ForeningDataForm(forms.Form):

    name = forms.CharField(required=True, error_messages={
        'required': "Foreningen må ha et navn!",
    })

    name.widget.attrs.update({
        'class': 'form-control'
    })

    post_address = forms.CharField(required=False)

    post_address.widget.attrs.update({
        'class': 'form-control'
    })

    visit_address = forms.CharField(required=False)

    visit_address.widget.attrs.update({
        'class': 'form-control'
    })

    zipcode = forms.CharField()

    counties = forms.ModelMultipleChoiceField(
        required=False,
        queryset=County.typical_objects().order_by('name')
    )

    counties.widget.attrs.update({
        'class': 'form-control',
        'data-chosen': '',
        'data-placeholder': 'Velg tilhørende fylke(r)...',
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
