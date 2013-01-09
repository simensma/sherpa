(function(ArticleWidgetEditor, $, undefined ) {

    var widget_editor; // Gets set in the preparations below

    /* New widget */

    $(document).on('widget.new.articles', function() {
        widget_editor.modal();
    });

    /* Editing existing widget */

    $(document).on('widget.edit', 'div.widget.articles', function() {
        widgetBeingEdited = $(this);
        widget_editor.modal();
        var widget = JSON.parse($(this).attr('data-json'));

        widget_editor.find("input[name='title']").val(widget.title);
        widget_editor.find("input[name='count']").val(widget.count);
        if(widget.tag_link == null) {
            widget_editor.find("input[name='set-tag-link'").removeAttr('checked');
            widget_editor.find("input[name='tag-link']").attr('disabled', true).val("");
        }
        article_widget_tagger.tags = widget.tags;
        var box = widget_editor.find("div.tag-box");
        box.empty();
        for(var i=0; i<widget.tags.length; i++) {
            var tag = $('<div class="tag"><a href="javascript:undefined"><img src="/static/img/so/close-default.png"></a> ' + widget.tags[i] + '</div>');
            box.append(tag);
        }
        if(widget.tags.length > 0) {
            widget_editor.find("input[name='enable-tags']").attr('checked', true);
            widget_editor.find("input[name='tags']").removeAttr('disabled');
        } else {
            widget_editor.find("input[name='enable-tags']").removeAttr('checked');
            widget_editor.find("input[name='tags']").attr('disabled', true);
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
                    url: '/tags/filter/',
                    data: 'name=' + encodeURIComponent(query)
                }).done(function(result) {
                    process(JSON.parse(result));
                });
            }
        });
        widget_editor.find("input[name='set-tag-link']").change(function() {
            if($(this).is(':checked')) {
                widget_editor.find("input[name='tag-link']").removeAttr('disabled');
            } else {
                widget_editor.find("input[name='tag-link']").attr('disabled', true).val("");
            }
        });

        widget_editor.find("input[name='enable-tags']").change(function() {
            if($(this).is(':checked')) {
                widget_editor.find("input[name='tags']").removeAttr('disabled');
            } else {
                widget_editor.find("input[name='tags']").attr('disabled', true).val("");
                widget_editor.find("div.tag-box").empty();
            }
        });

        // Create the tagger object, make it globally accessible
        window.article_widget_tagger = new TypicalTagger(widget_editor.find("input[name='tags']"), widget_editor.find("div.tag-box"));

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
            if(widget_editor.find("input[name='set-tag-link']").is(':checked')) {
                var tag_link = widget_editor.find("input[name='tag-link']").val();
            } else {
                var tag_link = null;
            }
            if(widget_editor.find("input[name='enable-tags']:checked").length > 0) {
                var tags = article_widget_tagger.tags;
            } else {
                var tags = [];
            }

            saveWidget({
                widget: "articles",
                title: title,
                tag_link: tag_link,
                tags: tags,
                count: count
            });
            widget_editor.modal('hide');
        });

    });

}(window.ArticleWidgetEditor = window.ArticleWidgetEditor || {}, jQuery ));
