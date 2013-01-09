/* Editing widgets */
$(document).ready(function() {

    // Save any widget
    $("div.widget-editor button.save").click(function() {
        var content = validateContent($(this).parents("div.widget-editor"));
        if(content === false) {
            return $(this);
        }
        $("div.widget-editor").modal('hide');
        saveWidget(content);
    });

    // Remove any widget
    $("div.widget-editor button.remove").click(function() {
        $(this).parents(".widget-editor").modal('hide');
        if(widgetBeingEdited != undefined){
            removeContent(widgetBeingEdited);
        }
    });

});

function saveWidget(content) {
    var rendring_message = '<img src="/static/img/ajax-loader-small.gif" alt="Laster..."> <em>Rendrer widget...</em>';
    var content_json = JSON.stringify(content);
    if(widgetBeingEdited !== undefined) {
        widgetBeingEdited.empty().append(rendring_message);
        widgetBeingEdited.attr('data-json', content_json);
        $.ajaxQueue({
            url: '/sherpa/cms/widget/',
            data: { content: content_json }
        }).done(function(result) {
            widgetBeingEdited.empty().append(result);
            disableIframes(widgetBeingEdited);
        });
    } else {
        var wrapper = $('<div class="content widget ' + content.widget + '"></div>');
        wrapper.append(rendring_message);
        wrapper.attr('data-json', content_json);
        if(widgetPosition.prev.length == 0) {
            widgetPosition.parent.prepend(wrapper);
        } else {
            widgetPosition.prev.after(wrapper);
        }
        removeEmpties();
        setEmpties();
        $.ajaxQueue({
            url: '/sherpa/cms/widget/',
            data: { content: content_json }
        }).done(function(result) {
            wrapper.empty().append(result);
            disableIframes(wrapper);
            refreshSort();
        });
    }
}

function validateContent(widget) {
    if(widget.attr('data-widget') == 'quote') {
        return {
            widget: "quote",
            quote: widget.find("textarea[name='quote']").val(),
            author: widget.find("input[name='author']").val()
        };
    } else if(widget.attr('data-widget') == 'carousel') {
        ImageCarouselWidgetEditor.saveCropping();
        return ImageCarouselWidgetEditor.validateContent();

    } else if(widget.attr('data-widget') == 'articles') {
        var count = widget.find("input[name='count']").val();
        if(isNaN(Number(count))) {
            alert("Du må angi et tall for antall nyheter som skal vises!");
            return false;
        } else if(count < 1) {
            alert("Du må vise minst én nyhet!");
            return false;
        }
        var title = widget.find("input[name='title']").val();
        if(widget.find("input[name='set-tag-link']").is(':checked')) {
            var tag_link = widget.find("input[name='tag-link']").val();
        } else {
            var tag_link = null;
        }
        if(widget.find("input[name='enable-tags']:checked").length > 0) {
            var tags = article_widget_tagger.tags;
        } else {
            var tags = [];
        }
        return {
            widget: "articles",
            title: title,
            tag_link: tag_link,
            tags: tags,
            count: count
        };
    } else if(widget.attr('data-widget') == 'blog') {
        var count = widget.find("input[name='count']").val();
        var category = widget.find("select[name='category']").val();

        if(isNaN(Number(count))) {
            alert("Du må angi et tall for antall blogginnlegg som skal vises!");
            return false;
        } else if(count < 1) {
            alert("Du må vise minst ett blogginnlegg!");
            return false;
        }
        return {
            widget: "blog",
            count: count,
            category : category
        };
    } else if(widget.attr('data-widget') == 'embed') {
        var code = widget.find("textarea[name='code']").val();
        if(code == '') {
            alert("Du må jo legge inn koden du vil bruke først! Hvis du ikke vil bruke widgeten likevel, trykk på 'Slett widget'-knappen.");
            return false;
        }
        return {
            widget: "embed",
            code: code
        };
    } else if(widget.attr('data-widget') == 'fact') {
        var content = widget.find("div.content").html();
        return {
            widget: "fact",
            content: content
        };
    }
}
