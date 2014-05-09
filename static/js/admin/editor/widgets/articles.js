$(function() {

    WidgetEditor.listen({
        widget_name: 'articles',

        init: function(editor) {
            // Enable/disable
            var url = editor.find("input[name='tag-link']").attr('data-tags-url');
            editor.find("input[name='tag-link']").typeahead({
                minLength: 3,
                remote: url + "?q=%QUERY"
            });
            editor.find("input[name='set-tag-link']").change(function() {
                if($(this).is(':checked')) {
                    editor.find("input[name='tag-link']").prop('disabled', false);
                } else {
                    editor.find("input[name='tag-link']").prop('disabled', true).val("");
                }
            });

            editor.find("input[name='enable-tags']").change(function() {
                if($(this).is(':checked')) {
                    editor.find("input[name='tags']").prop('disabled', false);
                } else {
                    editor.find("input[name='tags']").prop('disabled', true).val("");
                    editor.find("div.tag-box").empty();
                }
            });

            TagDisplay.enable({
                ref: 'article_widget',
                tagBox: editor.find("div.tag-box"),
                pickerInput: editor.find("input[name='tags']")
            });
        },

        onNew: function(editor) {
            TagDisplay.reset('article_widget');
        },

        onEdit: function(editor, widget_content) {
            editor.find("input[name='title']").val(widget_content.title);
            editor.find("input[name='count']").val(widget_content.count);
            editor.find("input[name='display-images']").prop('checked', widget_content.display_images);
            if(widget_content.tag_link === null) {
                editor.find("input[name='set-tag-link']").prop('checked', false);
                editor.find("input[name='tag-link']").prop('disabled', true).val("");
            }
            var tag_box = editor.find("div.tag-box");
            tag_box.attr('data-predefined-tags', JSON.stringify(widget_content.tags));
            TagDisplay.reset('article_widget');
            if(widget_content.tags.length > 0) {
                editor.find("input[name='enable-tags']").prop('checked', true);
                editor.find("input[name='tags']").prop('disabled', false);
            } else {
                editor.find("input[name='enable-tags']").prop('checked', false);
                editor.find("input[name='tags']").prop('disabled', true);
            }
        },

        onSave: function(editor) {
            var count = editor.find("input[name='count']").val();
            if(isNaN(Number(count))) {
                alert("Du må angi et tall for antall nyheter som skal vises!");
                return false;
            } else if(count < 1) {
                alert("Du må vise minst én nyhet!");
                return false;
            }
            var title = editor.find("input[name='title']").val();
            var display_images = editor.find("input[name='display-images']").prop('checked');
            if(editor.find("input[name='set-tag-link']").is(':checked')) {
                var tag_link = editor.find("input[name='tag-link']").val();
            } else {
                var tag_link = null;
            }
            if(editor.find("input[name='enable-tags']:checked").length > 0) {
                var tags = TagDisplay.getTags('article_widget');
            } else {
                var tags = [];
            }

            WidgetEditor.saveWidget({
                widget: "articles",
                title: title,
                display_images: display_images,
                tag_link: tag_link,
                tags: tags,
                count: count,
            });
            return true;
        }
    });
});
