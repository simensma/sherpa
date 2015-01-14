# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Enrollment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('state', models.CharField(max_length=255)),
                ('accepts_conditions', models.BooleanField(default=False)),
                ('partneroffers_optin', models.BooleanField(default=False)),
                ('existing_memberid', models.CharField(max_length=51)),
                ('wants_yearbook', models.BooleanField(default=False)),
                ('attempted_yearbook', models.BooleanField(default=False)),
                ('payment_method', models.CharField(max_length=51)),
                ('result', models.CharField(max_length=255)),
                ('country', models.CharField(max_length=2)),
                ('address1', models.CharField(max_length=255)),
                ('address2', models.CharField(max_length=255)),
                ('address3', models.CharField(max_length=255)),
                ('zipcode', models.CharField(max_length=51)),
                ('area', models.CharField(max_length=255)),
                ('date_initiated', models.DateTimeField(auto_now_add=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='State',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('active', models.BooleanField(default=True)),
                ('card', models.BooleanField(default=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('transaction_id', models.CharField(max_length=32)),
                ('order_number', models.CharField(max_length=32)),
                ('active', models.BooleanField(default=False)),
                ('state', models.CharField(default=b'register', max_length=255, choices=[(b'register', b'Startet, men ikke gjennomf\xc3\xb8rt'), (b'cancel', b'Avbrutt av kunden'), (b'fail', b'Avsl\xc3\xa5tt av banken'), (b'success', b'Betaling godkjent')])),
                ('initiated', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ['-initiated'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=511)),
                ('phone', models.CharField(max_length=255)),
                ('email', models.CharField(max_length=511)),
                ('gender', models.CharField(max_length=1)),
                ('key', models.BooleanField(default=False)),
                ('dob', models.DateField(null=True)),
                ('chosen_main_member', models.BooleanField(default=False)),
                ('memberid', models.IntegerField(null=True)),
                ('sms_sent', models.BooleanField(default=False)),
                ('enrollment', models.ForeignKey(related_name=b'users', to='enrollment.Enrollment')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
