# encoding: utf-8
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse

from smtplib import SMTPDataError

EMAIL_FROM = "Den Norske Turistforening <medlem@turistforeningen.no>"
EMAIL_SUBJECT = "Gavemedlemskap"

# Hardcoded ages
AGE_SENIOR = 67
AGE_MAIN = 27
AGE_STUDENT = 19
AGE_SCHOOL = 13

def index(request):
    context = {}
    return render(request, 'enrollment/gift.html', context)

