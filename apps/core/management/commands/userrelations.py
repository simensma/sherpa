# encoding: utf-8
from django.core.management.base import BaseCommand
from django.db import models

class Command(BaseCommand):
    args = u""
    help = u"List relasjoner til user.User"

    def handle(self, *args, **options):
        formatted_output = {}
        for model in models.get_models():
            output_fields = []
            for field in (model._meta.fields + model._meta.local_many_to_many):
                if hasattr(field, 'related') and field.rel.get_related_field().model._meta.object_name == 'User':
                    output_fields.append("%s: %s" % (field.name, field))
            if len(output_fields) > 0:
                formatted_output["%s.%s" % (model._meta.app_label, model._meta.object_name)] = output_fields

        for model, fields in sorted(formatted_output.items(), key=lambda m: m[0].split('.')[1]):
            print("%s:" % model)
            for field in fields:
                print("  %s" % field)
            print("")
