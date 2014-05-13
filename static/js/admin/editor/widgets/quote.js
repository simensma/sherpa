$(function() {

    WidgetEditor.listen({
        widget_name: 'quote',

        onEdit: function(editor, widget_content) {
            editor.find("textarea[name='quote']").val(widget_content.quote);
            editor.find("input[name='author']").val(widget_content.author);
        },

        onSave: function(editor) {
            WidgetEditor.saveWidget({
                widget: "quote",
                quote: editor.find("textarea[name='quote']").val(),
                author: editor.find("input[name='author']").val()
            });
            return true;
        }
    });

});
