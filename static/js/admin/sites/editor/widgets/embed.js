$(function() {

    WidgetEditor.listen({
        widget_name: 'embed',

        onEdit: function(editor, widget_content) {
            editor.find("textarea[name='code']").text(widget_content.code);
        },

        onSave: function(editor) {
            var code = editor.find("textarea[name='code']").val();
            if(code === '') {
                alert("Du må jo legge inn koden du vil bruke først! Hvis du ikke vil bruke widgeten likevel, lukk vinduet med krysset oppe til høyre.");
                return false;
            }
            WidgetEditor.saveWidget({
                widget: "embed",
                code: code
            });
            return true;
        }
    });

});
