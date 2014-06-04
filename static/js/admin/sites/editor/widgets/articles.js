$(function() {

    WidgetEditor.listen({
        widget_name: 'articles',

        init: function(editor) {
            editor.find("input[name='layout']").click(function() {
                if(editor.find("input[name='layout']:checked").val() === 'medialist') {
                    editor.find("div.medialist-section").show();
                    editor.find("div.horizontal-section").hide();
                } else {
                    editor.find("div.medialist-section").hide();
                    editor.find("div.horizontal-section").show();
                }
            });

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
            editor.find("input[name='layout'][value='" + widget_content.layout + "']").prop('checked', True);
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
            var layout = editor.find("input[name='layout']:checked").val();

            var title;
            var count;
            var columns;
            if(layout === 'medialist') {
                count = editor.find("input[name='count']").val();
                if(isNaN(Number(count))) {
                    alert("Du må angi et tall for antall nyheter som skal vises!");
                    return false;
                } else if(count < 1) {
                    alert("Du må vise minst én nyhet!");
                    return false;
                }
                title = editor.find("input[name='title']").val();

                // Set unused default value for columns
                columns = 2;
            } else if(layout === 'horizontal') {
                columns = editor.find("select[name='columns'] option:selected").val();

                // Set unused default value for count/title
                count = 1;
                title = '';
            } else {
                alert("Du må velge om visningen skal være stående eller liggende.");
                return false;
            }

            var display_images = editor.find("input[name='display-images']").prop('checked');
            var tag_link;
            if(editor.find("input[name='set-tag-link']").is(':checked')) {
                tag_link = editor.find("input[name='tag-link']").val();
            } else {
                tag_link = null;
            }
            var tags;
            if(editor.find("input[name='enable-tags']:checked").length > 0) {
                tags = TagDisplay.getTags('article_widget');
            } else {
                tags = [];
            }

            WidgetEditor.saveWidget({
                widget: "articles",
                layout: layout,
                title: title,
                count: count,
                columns: columns,
                display_images: display_images,
                tag_link: tag_link,
                tags: tags,
            });
            return true;
        }
    });
});
