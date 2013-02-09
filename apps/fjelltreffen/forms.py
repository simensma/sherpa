# encoding: utf-8
from django import forms
from django.forms.widgets import Textarea
from captcha.fields import CaptchaField

class ReplyForm(forms.Form):

    name = forms.CharField()
    email = forms.EmailField()
    text = forms.CharField(widget=Textarea)

    name.widget.attrs.update({
        'placeholder': "Ditt navn...",
        'class': 'input-xlarge'
        })

    email.widget.attrs.update({
        'placeholder': "Din e-postadresse...",
        'class': 'input-xlarge'
        })

    text.widget.attrs.update({
        'placeholder': "Skriv svaret ditt her..."
        })

    def __init__(self, *args, **kwargs):
        super(ReplyForm, self).__init__(*args, **kwargs)
        self.fields['name'].error_messages = {
            'required': 'Du må oppgi navnet ditt!'}

        self.fields['email'].error_messages = {
            'required': 'Du må oppgi e-postadressen din, uten denne kan ikke annonsøren svare deg!',
            'invalid': 'Du må skrive inn en gyldig e-postadresse, uten denne kan ikke annonsøren svare deg!'}

        self.fields['text'].error_messages = {
            'required': 'Du må da skrive litt i svaret til annonsøren!'}

# Anonymous users must also fill a Captcha
class ReplyAnonForm(ReplyForm):

    captcha = CaptchaField()

    def __init__(self, *args, **kwargs):
        super(ReplyAnonForm, self).__init__(*args, **kwargs)
        self.fields['captcha'].error_messages = {
            'required': 'Du må fylle inn bokstavene i bildet.',
            'invalid': 'Du skrev bokstavene som stod i bildet riktig, vennligst prøv igjen.'}
