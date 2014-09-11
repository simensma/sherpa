class Widget(object):
    def parse(self, widget_options, site):
        """Reads the provided widget options and returns a parsed widget - the data which needs to be
        calculated server-side. Must be implemented."""
        raise NotImplementedError

    def admin_context(self, site):
        """Optional: Implement to return context data which is needed in the admin editor when editing the widget"""
        return {}
