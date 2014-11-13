# encoding: utf-8
from django import forms

from foreninger.models import Forening

class SiteForm(forms.Form):

    forening = forms.IntegerField(required=True)

    def __init__(self, user, *args, **kwargs):
        super(SiteForm, self).__init__(*args, **kwargs)
        self._user = user

    def clean_forening(self):
        forening = Forening.objects.get(id=self.cleaned_data['forening'])
        if forening not in self._user.all_foreninger():
            # Should never happen unless the POST request is forged
            raise forms.ValidationError("Du har ikke tilgang til denne foreningen")
        return forening
