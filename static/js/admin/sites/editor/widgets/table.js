$(function() {

    WidgetEditor.listen({
        widget_name: 'table',

        init: function(editor) {},
        onEdit: function(editor, widget_content) {},

        onSave: function(editor) {
            WidgetEditor.saveWidget({
                widget: "table",
            });
            return true;
        }
    });

});
