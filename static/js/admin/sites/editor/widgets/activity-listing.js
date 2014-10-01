$(function() {

    WidgetEditor.listen({
        widget_name: 'activity-listing',

        init: function(editor) {
        },

        onNew: function(editor) {
        },

        onEdit: function(editor, widget_content) {
        },

        onSave: function(editor) {
            WidgetEditor.saveWidget({
                widget: 'activity-listing',
            });
            return true;
        }
    });
});
