from django import template

import md5

from user.models import Profile, AssociationRole
from association.models import Association

register = template.Library()

class RoleNode(template.Node):
    def __init__(self, profile, association):
        self.profile = template.Variable(profile)
        self.association = template.Variable(association)

    def render(self, context):
        try:
            profile = self.profile.resolve(context)
            association = self.association.resolve(context)
            return AssociationRole.friendly_role(AssociationRole.objects.get(profile=profile, association=association).role)
        except template.VariableDoesNotExist:
            return ''

@register.tag
def associationrole(parser, token):
    try:
        tag_name, profile, association = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError("%r tag requires exactly 2 arguments" % token.contents.split()[0])
    return RoleNode(profile, association)
