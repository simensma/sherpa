# encoding: utf-8
import logging
import re

from django import forms

from core.models import Site
from foreninger.models import Forening

logger = logging.getLogger('sherpa')

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
    template_type = forms.ChoiceField(
        required=False,
        choices=Site.TEMPLATE_TYPE_CHOICES,
    )
    template_main = forms.BooleanField(required=False)
    template_description = forms.CharField(required=False)

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

    def clean_template_description(self):
        return self.cleaned_data['template_description'].strip()

    def clean(self):
        cleaned_data = super(SiteForm, self).clean()
        edited_site = cleaned_data.get("edited_site")
        forening = cleaned_data.get("forening")
        type = cleaned_data.get("type")
        title = cleaned_data.get("title")
        template_type = cleaned_data.get("template_type")
        template_main = cleaned_data.get("template_main")
        template_description = cleaned_data.get("template_description")

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
                cleaned_data['title'] = title
            else:
                cleaned_data['title'] = ''

            if type == 'mal':
                # Since the fields aren't required by default but *are* required in this case; check explicitly
                if template_type is None or template_main is None or template_description is None:
                    # Don't ever expect this to happen
                    self._errors['template_type'] = self.error_class([
                        "Du har valgt å opprette en mal uten å sende med informasjon om malen!"
                    ])
            else:
                cleaned_data['template_main'] = False
                cleaned_data['template_type'] = ''
                cleaned_data['template_description'] = ''

        return cleaned_data

class CreateSiteForm(SiteForm):
    domain = forms.CharField(
        error_messages={
            'required': "Du må velge et midlertidig domene for nettstedet.",
        }
    )

    def clean_domain(self):
        domain = self.cleaned_data['domain'].strip().lower()
        domain = re.sub('https?://', '', domain)
        domain = domain.strip('/').strip('.')

        # Requiring test-domain at the moment
        domain = '%s.test.turistforeningen.no' % domain

        result = Site.verify_domain(domain)

        if not result['valid']:
            if result['error'] == 'malformed':
                raise forms.ValidationError(
                    u"Du må fylle inn et gyldig domenenavn. Hør med DNT sentralt dersom du er usikker på hva dette bør være.",
                    code=result['error'],
                )
            elif result['error'] == 'more_than_one_subdir':
                raise forms.ValidationError(
                    u"Du kan ikke ha to undermapper i domenenavnet. Hør med DNT sentralt dersom du er usikker på hva domenenavnet deres er.",
                    code=result['error'],
                )
            elif result['error'] == 'prefix_for_disallowed_domain':
                main_site = Site.objects.get(id=Site.DNT_CENTRAL_ID)
                raise forms.ValidationError(
                    u"Kun domener direkte under <strong>%s</strong> kan ha undermapper. Hør med DNT sentralt dersom du er usikker på hva domenenavnet deres er." % main_site.domain,
                    code=result['error'],
                )
            elif result['error'] == 'site_exists':
                raise forms.ValidationError(
                    u"<strong>%s</strong> har allerede domenenavnet <strong>http://{{ existing_domain }}/</strong>. Hør med DNT sentralt dersom du er usikker på hva domenenavnet deres er." % result['existing_forening'].name,
                    code=result['error'],
                )
            elif result['error'] == 'prefix_not_supported_yet':
                main_site = Site.objects.get(id=Site.DNT_CENTRAL_ID)
                raise forms.ValidationError(
                    u"Domenet kan ikke være en undermappe under turistforeningen.no (for eksempel: <strong>%s/mitt-turlag</strong>) fordi vi ikke har satt opp teknisk støtte for det ennå." % main_site.domain,
                    code=result['error'],
                )
            elif result['error'] == 'test_period_requires_test_domain':
                # Shouldn't happen since we're explicitly appending the test-domain, but handle it nevertheless
                raise forms.ValidationError(
                    u"I test-perioden <strong>må</strong> dere ha \"<strong>.test.turistforeningen.no</strong>\" bak domenet. For eksempel: <strong>http://stf.test.turistforeningen.no</strong>.",
                    code=result['error'],
                )
            else:
                # Unknown verify_domain error code :(
                logger.error(u"Ukjent domenevaliderings-feilkode '%s'" % result['error'])
                raise forms.ValidationError(
                    u"Domeneadressen er ikke gyldig, dobbeltsjekk at du har skrevet riktig",
                    code=result['error'],
                )
        else:
            return (result['domain'], result['prefix'])
