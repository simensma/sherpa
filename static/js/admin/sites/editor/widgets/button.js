$(function() {

    var preview_button;

    WidgetEditor.listen({
        widget_name: 'button',

        init: function(editor) {
            preview_button = editor.find('[data-dnt-preview-button]');
            preview_button.text(preview_button.attr('data-dnt-placeholder'));

            editor.find('input[name="text"]').keyup(function() {
                var text = $(this).val().trim();
                if(text === '') {
                    text = preview_button.attr('data-dnt-placeholder');
                }
                preview_button.text(text);
            });

            editor.find('input[name="color"]').change(function() {
                preview_button.removeClass('btn-default btn-danger');
                preview_button.addClass($(this).val());
            });

            editor.find('input[name="size"]').change(function() {
                preview_button.removeClass('btn-lg');
                preview_button.addClass($(this).val());
            });
        },

        onNew: function(editor) {
            editor.find("input[name='text']").val('');
            editor.find("input[name='url']").val('http://');
            editor.find("input[name='color'][value='btn-default']").prop('checked', true);
            editor.find("input[name='size'][value='']").prop('checked', true);
        },

        onEdit: function(editor, widget_content) {
            editor.find("input[name='text']").val(widget_content.text);
            editor.find("input[name='url']").val(widget_content.url);
            editor.find("input[name='color'][value='" + widget_content.color + "']").prop('checked', true);
            editor.find("input[name='size'][value='" + widget_content.size + "']").prop('checked', true);

            // Trigger preview button updates
            editor.find("input[name='text']").keyup();
            editor.find("input[name='color']:checked").change();
            editor.find("input[name='size']:checked").change();
        },

        onSave: function(editor) {
            var text = editor.find("input[name='text']").val().trim();
            var url = editor.find("input[name='url']").val().trim();
            if(text === "") {
                alert(editor.attr('data-no-text-warning'));
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

