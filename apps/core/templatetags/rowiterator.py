from django import template

register = template.Library()

@register.tag()
def rowiterator(parser, token):
    nodelist = parser.parse(('endrowiterator',))
    tag_name, columns = token.split_contents()
    parser.delete_first_token()
    return IteratorNode(nodelist, int(columns))

class IteratorNode(template.Node):
    def __init__(self, nodelist, columns):
        self.nodelist = nodelist
        self.columns = columns

    def render(self, context):
        context.render_context['rowiterator_columns'] = self.columns
        return '<div class="row">%s</div>' % self.nodelist.render(context)

@register.tag()
def column(parser, token):
    nodelist = parser.parse(('endcolumn',))
    parser.delete_first_token()
    return ColumnNode(nodelist)

class ColumnNode(template.Node):
    def __init__(self, nodelist):
        self.nodelist = nodelist

    def render(self, context):
        columns = context.render_context['rowiterator_columns']
        new_row = False
        if not 'rowiterator_row' in context.render_context:
            context.render_context['rowiterator_row'] = 1
        elif context.render_context['rowiterator_row'] == columns:
            context.render_context['rowiterator_row'] = 1
            new_row = True
        else:
            context.render_context['rowiterator_row'] += 1

        output = '<div class="span%s">%s</div>' % ((12 / columns), self.nodelist.render(context))
        if new_row:
            return '</div><div class="row">%s' % (output)
        else:
            return output
