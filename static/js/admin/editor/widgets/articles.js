(function(ArticleWidgetEditor, $, undefined ) {

    var widget_editor; // Gets set in the preparations below

    /* New widget */

    $(document).on('widget.new.articles', function() {
        widget_editor.modal();
        TagDisplayAH.reset('article_widget');
    });

    /* Editing existing widget */

    $(document).on('widget.edit', 'div.widget.articles', function() {
        widgetBeingEdited = $(this);
        widget_editor.modal();
        var widget = JSON.parse($(this).attr('data-json'));

        widget_editor.find("input[name='title']").val(widget.title);
        widget_editor.find("input[name='count']").val(widget.count);
        widget_editor.find("input[name='display-images']").prop('checked', widget.display_images);
        if(widget.tag_link == null) {
            widget_editor.find("input[name='set-tag-link']").prop('checked', false);
            widget_editor.find("input[name='tag-link']").prop('disabled', true).val("");
        }
        var tag_box = widget_editor.find("div.tag-box");
        tag_box.attr('data-predefined-tags', JSON.stringify(widget.tags));
        TagDisplayAH.reset('article_widget');
        if(widget.tags.length > 0) {
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
        widget_editor.find("input[name='tag-link']").typeahead({
            minLength: 3,
            source: function(query, process) {
                $.ajaxQueue({
                    url: widget_editor.find("input[name='tag-link']").attr('data-source-url'),
                    data: { name: query }
                }).done(function(result) {
                    process(JSON.parse(result));
                });
            }
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

        TagDisplayAH.enable({
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
                var tags = TagDisplayAH.getTags('article_widget');
            } else {
                var tags = [];
            }

            saveWidget(widgetBeingEdited, {
                widget: "articles",
                title: title,
                display_images: display_images,
                tag_link: tag_link,
                tags: tags,
                count: count
            });
            widget_editor.modal('hide');
        });

    });

}(window.ArticleWidgetEditor = window.ArticleWidgetEditor || {}, jQuery ));
