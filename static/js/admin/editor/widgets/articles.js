(function(ArticleWidgetEditor, $, undefined ) {

    var widget_editor; // Gets set in the preparations below
    var editor_callback; // Sent with the trigger from the editor

    /* New widget */

    $(document).on('widget.new.articles', function(e, _editor_callback) {
        editor_callback = _editor_callback;
        widget_editor.modal();
        TagDisplay.reset('article_widget');
    });

    /* Editing existing widget */

    $(document).on('widget.edit', 'div.widget.articles', function(e, widget_content, _editor_callback) {
        editor_callback = _editor_callback;
        widget_editor.modal();
        widget_editor.find("input[name='title']").val(widget_content.title);
        widget_editor.find("input[name='count']").val(widget_content.count);
        widget_editor.find("input[name='display-images']").prop('checked', widget_content.display_images);
        if(widget_content.tag_link === null) {
            widget_editor.find("input[name='set-tag-link']").prop('checked', false);
            widget_editor.find("input[name='tag-link']").prop('disabled', true).val("");
        }
        var tag_box = widget_editor.find("div.tag-box");
        tag_box.attr('data-predefined-tags', JSON.stringify(widget_content.tags));
        TagDisplay.reset('article_widget');
        if(widget_content.tags.length > 0) {
            widget_editor.find("input[name='enable-tags']").prop('checked', true);
            widget_editor.find("input[name='tags']").prop('disabled', false);
        } else {
            widget_editor.find("input[name='enable-tags']").prop('checked', false);
            widget_editor.find("input[name='tags']").prop('disabled', true);
        }
    });

    /* Document preparations */

    $(document).ready(function() {

        widget_editor = $("div.widget-editor[data-widget='articles']");

        // Enable/disable
        var url = widget_editor.find("input[name='tag-link']").attr('data-tags-url');
        widget_editor.find("input[name='tag-link']").typeahead({
            minLength: 3,
            remote: url + "?q=%QUERY"
        });
        widget_editor.find("input[name='set-tag-link']").change(function() {
            if($(this).is(':checked')) {
                widget_editor.find("input[name='tag-link']").prop('disabled', false);
            } else {
                widget_editor.find("input[name='tag-link']").prop('disabled', true).val("");
            }
        });

        widget_editor.find("input[name='enable-tags']").change(function() {
            if($(this).is(':checked')) {
                widget_editor.find("input[name='tags']").prop('disabled', false);
            } else {
                widget_editor.find("input[name='tags']").prop('disabled', true).val("");
                widget_editor.find("div.tag-box").empty();
            }
        });

        TagDisplay.enable({
            ref: 'article_widget',
            tagBox: widget_editor.find("div.tag-box"),
            pickerInput: widget_editor.find("input[name='tags']")
        });

        /* Saving */
        widget_editor.find("button.save").click(function() {
            var count = widget_editor.find("input[name='count']").val();
            if(isNaN(Number(count))) {
                alert("Du må angi et tall for antall nyheter som skal vises!");
                return $(this);
            } else if(count < 1) {
                alert("Du må vise minst én nyhet!");
                return $(this);
            }
            var title = widget_editor.find("input[name='title']").val();
            var display_images = widget_editor.find("input[name='display-images']").prop('checked');
            if(widget_editor.find("input[name='set-tag-link']").is(':checked')) {
                var tag_link = widget_editor.find("input[name='tag-link']").val();
            } else {
                var tag_link = null;
            }
            if(widget_editor.find("input[name='enable-tags']:checked").length > 0) {
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
            }, editor_callback);
            widget_editor.modal('hide');
        });

    });

}(window.ArticleWidgetEditor = window.ArticleWidgetEditor || {}, jQuery ));
