$(function() {

    WidgetEditor.listen({
        widget_name: 'button',

        init: function(editor) {
            editor.find("table.choices button").click(function() {
                $(this).parent().prev().children("input[type='radio']").click();
            });
        },

        onEdit: function(editor, widget_content) {
            editor.find("input[name='url']").val(widget_content.url);
        },

        onSave: function(editor) {
            var text = editor.find("input[name='text']").val().trim();
            var url = editor.find("input[name='url']").val().trim();
            if(text === "") {
                editor.find("div.alert").show();
                return false;
            }

            if(!url.match(/^https?:\/\//)) {
                url = "http://" + url;
            }

            var color = editor.find("input[name='color']:checked").val();
            var size = editor.find("input[name='size']:checked").val();

            WidgetEditor.saveWidget({
                widget: "button",
                text: text,
                url: url,
                color: color,
                size: size,
            });
            return true;
        }
    });
});

