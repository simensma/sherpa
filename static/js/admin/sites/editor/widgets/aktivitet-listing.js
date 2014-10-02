$(function() {

    WidgetEditor.listen({
        widget_name: 'aktivitet-listing',

        init: function(editor) {
        },

        onNew: function(editor) {
        },

        onEdit: function(editor, widget_content) {
        },

        onSave: function(editor) {
            WidgetEditor.saveWidget({
                widget: 'aktivitet-listing',
            });
            return true;
        }
    });
});
