import random

from page.widgets.widget import Widget

class CarouselWidget(Widget):
    def parse(self, widget_options, site):
        # NO! BAD HAVARD, dont use hax, create an id(but not now)
        return {
            'id':random.randint(0,10000),
            'images':widget_options['images'],
        }
