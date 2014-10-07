# encoding: utf-8
from django import forms
from django.forms.widgets import Textarea

from captcha.fields import ReCaptchaField

class ReplyForm(forms.Form):

    name = forms.CharField()
    email = forms.EmailField()
    text = forms.CharField(widget=Textarea)

    name.widget.attrs.update({
        'placeholder': "Ditt navn...",
        'class': 'form-control',
    })

    email.widget.attrs.update({
        'placeholder': "Din e-postadresse...",
        'class': 'form-control',
    })

    text.widget.attrs.update({
        'placeholder': "Skriv svaret ditt her...",
        'class': 'form-control',
    })

    def __init__(self, *args, **kwargs):
        super(ReplyForm, self).__init__(*args, **kwargs)
        self.fields['name'].error_messages = {
            'required': 'Du må oppgi navnet ditt!'
        }

        self.fields['email'].error_messages = {
            'required': 'Du må oppgi e-postadressen din, uten denne kan ikke annonsøren svare deg!',
            'invalid': 'Du må skrive inn en gyldig e-postadresse, uten denne kan ikke annonsøren svare deg!'
        }

        self.fields['text'].error_messages = {
            'required': 'Du må da skrive litt i svaret til annonsøren!'
        }

# Anonymous users must also fill a Captcha
class ReplyAnonForm(ReplyForm):

    captcha = ReCaptchaField()

    def __init__(self, *args, **kwargs):
        super(ReplyAnonForm, self).__init__(*args, **kwargs)
        self.fields['captcha'].error_messages = {
            'required': 'Du må fylle inn bokstavene i bildet.',
            'captcha_invalid': 'Du skrev ikke bokstavene som stod i bildet riktig, vennligst prøv igjen.'
        }
