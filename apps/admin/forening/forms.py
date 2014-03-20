# encoding: utf-8
from django import forms

class ForeningDataForm(forms.Form):

    name = forms.CharField(required=True, error_messages={
        'required': "Foreningen må ha et navn!",
    })

    name.widget.attrs.update({
        'class': 'form-control'
    })

    def clean_name(self):
        return self.cleaned_data['name'].strip()
