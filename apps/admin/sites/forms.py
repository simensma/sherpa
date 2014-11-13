# encoding: utf-8
from django import forms

from core.models import Site
from foreninger.models import Forening

class SiteForm(forms.Form):

    edited_site = forms.IntegerField(required=False)
    forening = forms.IntegerField(required=True)
    type = forms.ChoiceField(
        required=True,
        choices=Site.TYPE_CHOICES,
        error_messages={
            'required': "Du må velge hva slags nettsted dette er",
        }
    )
    title = forms.CharField(required=False)

    def __init__(self, user, *args, **kwargs):
        super(SiteForm, self).__init__(*args, **kwargs)
        self._user = user

    def clean_edited_site(self):
        edited_site = self.cleaned_data.get('edited_site')
        if edited_site is not None:
            return Site.objects.get(id=edited_site)

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

    def clean_title(self):
        return self.cleaned_data['title'].strip()

    def clean(self):
        cleaned_data = super(SiteForm, self).clean()
        edited_site = cleaned_data.get("edited_site")
        forening = cleaned_data.get("forening")
        type = cleaned_data.get("type")
        title = cleaned_data.get("title")

        if forening is not None and type is not None:
            homepage = forening.get_homepage_site()
            if type == 'forening' and homepage is not None:
                if edited_site is None or edited_site != homepage:
                    # This forening already has *another* homepage. Shouldn't happen if the client-side logic works
                    # as it is supposed to.
                    self._errors['forening'] = self.error_class([
                        "%s har allerede en hjemmeside, du kan ikke sette opp en ny." % forening.name,
                    ])

        if type is not None:
            if type in ['hytte', 'kampanje', 'mal']:
                cleaned_data['title'] = title.strip()
            else:
                cleaned_data['title'] = ''

        return cleaned_data
