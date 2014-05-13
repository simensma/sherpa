$(function() {

    WidgetEditor.listen({
        widget_name: 'fact',

        onEdit: function(editor, widget_content) {
            editor.find("div.content").html(widget_content.content);
        },

        onSave: function(editor) {
            var content = editor.find("div.content").text();
            WidgetEditor.saveWidget({
                widget: "fact",
                content: content
            });
            return true;
        }
    });

});
