# encoding: utf-8
from django import forms

from core.models import Site
from foreninger.models import Forening

class SiteForm(forms.Form):

    forening = forms.IntegerField(required=True)
    type = forms.ChoiceField(
        required=True,
        choices=Site.TYPE_CHOICES,
        error_messages={
            'required': "Du må velge hva slags nettsted dette er",
        })

    def __init__(self, user, *args, **kwargs):
        super(SiteForm, self).__init__(*args, **kwargs)
        self._user = user

    def clean_forening(self):
        forening = Forening.objects.get(id=self.cleaned_data['forening'])
        if forening not in self._user.all_foreninger():
            # Should never happen unless the POST request is forged
            raise forms.ValidationError("Du har ikke tilgang til denne foreningen")
        return forening

    def clean_type(self):
        type = self.cleaned_data['type'].strip()
        if type == 'mal' and not self._user.has_perm('sherpa_admin'):
            raise forms.ValidationError("Du har ikke tilgang til denne nettstedstypen", code='unauthorized')
        return type
