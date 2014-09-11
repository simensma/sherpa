from page.widgets.widget import Widget

class TableWidget(Widget):
    def parse(self, widget_options, site):
        return {
            'header': widget_options['table'][0],
            'body': widget_options['table'][1:],
        }
