from page.widgets.widget import Widget

class QuoteWidget(Widget):
    def parse(self, widget_options, site):
        return {
            'quote': widget_options['quote'],
            'author': widget_options['author'],
        }
