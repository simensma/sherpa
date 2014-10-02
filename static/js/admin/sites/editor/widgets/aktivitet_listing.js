$(function() {

    WidgetEditor.listen({
        widget_name: 'aktivitet_listing',

        init: function(editor) {
        },

        onNew: function(editor) {
        },

        onEdit: function(editor, widget_content) {
        },

        onSave: function(editor) {
            WidgetEditor.saveWidget({
                widget: 'aktivitet_listing',
            });
            return true;
        }
    });
});
