from page.widgets.widget import Widget

class EmbedWidget(Widget):
    def parse(self, widget_options, site):
        return {'code': widget_options['code']}
