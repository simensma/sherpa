$(function() {

    var preview_button;
    var url_static_input;

    WidgetEditor.listen({
        widget_name: 'button',

        init: function(editor) {
            preview_button = editor.find('[data-dnt-preview-button]');
            url_static_input = editor.find('[data-dnt-input="url"]');

            preview_button.text(preview_button.attr('data-dnt-placeholder'));

            editor.find('input[name="text"]').keyup(function() {
                var text = $(this).val().trim();
                if(text === '') {
                    text = preview_button.attr('data-dnt-placeholder');
                }
                preview_button.text(text);
            });

            editor.find('[data-dnt-trigger="pick-url"]').click(function() {
                var existing_url;
                var url = url_static_input.text().trim();
                if(url !== url_static_input.attr('data-dnt-placeholder')) {
                    existing_url = url;
                }

                UrlPicker.open({
                    existing_url: existing_url,
                    done: function(result) {
                        url_static_input.text(result.url);
                    }
                });
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
            url_static_input.text(url_static_input.attr('data-dnt-placeholder'));
            editor.find("input[name='url']").val('http://');
            editor.find('[data-dnt-input="url"]').val('http://');
            editor.find("input[name='color'][value='btn-default']").prop('checked', true);
            editor.find("input[name='size'][value='']").prop('checked', true);
        },

        onEdit: function(editor, widget_content) {
            editor.find("input[name='text']").val(widget_content.text);
            url_static_input.text(widget_content.url);
            editor.find("input[name='color'][value='" + widget_content.color + "']").prop('checked', true);
            editor.find("input[name='size'][value='" + widget_content.size + "']").prop('checked', true);

            // Trigger preview button updates
            editor.find("input[name='text']").keyup();
            editor.find("input[name='color']:checked").change();
            editor.find("input[name='size']:checked").change();
        },

        onSave: function(editor) {
            var text = editor.find("input[name='text']").val().trim();
            var url = url_static_input.text().trim();

            if(text === "") {
                alert(editor.attr('data-no-text-warning'));
                return false;
            }

            if(url === url_static_input.attr('data-dnt-placeholder')) {
                alert(editor.attr('data-no-url-warning'));
                return false;
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

