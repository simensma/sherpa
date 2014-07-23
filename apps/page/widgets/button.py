from page.widgets.widget import Widget

class ButtonWidget(Widget):
    def parse(self, widget_options, site):
        return {
            'text': widget_options['text'],
            'url': widget_options['url'],
            'color': widget_options['color'],
            'size': widget_options['size'],
        }
