from page.widgets.widget import Widget

class FactWidget(Widget):
    def parse(self, widget_options, site):
        return {'content': widget_options['content']}
