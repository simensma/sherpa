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

    /* Articles */

    // Enable/disable
    var articles = $("div.widget-editor[data-widget='articles']");
    articles.find("input[name='tag-link']").typeahead({
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
    articles.find("input[name='set-tag-link']").change(function() {
        if($(this).is(':checked')) {
            articles.find("input[name='tag-link']").removeAttr('disabled');
        } else {
            articles.find("input[name='tag-link']").attr('disabled', true).val("");
        }
    });

    articles.find("input[name='enable-tags']").change(function() {
        if($(this).is(':checked')) {
            articles.find("input[name='tags']").removeAttr('disabled');
        } else {
            articles.find("input[name='tags']").attr('disabled', true).val("");
            articles.find("div.tag-box").empty();
        }
    });

    // Create the tagger object, make it globally accessible
    window.article_widget_tagger = new TypicalTagger(articles.find("input[name='tags']"), articles.find("div.tag-box"));

});

function saveWidget(content) {
    var rendring_message = '<img src="/static/img/ajax-loader-small.gif" alt="Laster..."> <em>Rendrer widget...</em>';
    if(widgetBeingEdited !== undefined) {
        widgetBeingEdited.empty().append(rendring_message);
        widgetBeingEdited.attr('data-json', content);
        $.ajaxQueue({
            url: '/sherpa/cms/widget/',
            data: { content: content }
        }).done(function(result) {
            widgetBeingEdited.empty().append(result);
            disableIframes(widgetBeingEdited);
        });
    } else {
        // Re-parse widget type for now - but later, have validateContent return an *object* content and stringify it here
        var widget_type = JSON.parse(content).widget;
        var wrapper = $('<div class="content widget ' + widget_type + '"></div>');
        wrapper.append(rendring_message);
        wrapper.attr('data-json', content);
        if(widgetPosition.prev.length == 0) {
            widgetPosition.parent.prepend(wrapper);
        } else {
            widgetPosition.prev.after(wrapper);
        }
        removeEmpties();
        setEmpties();
        $.ajaxQueue({
            url: '/sherpa/cms/widget/',
            data: { content: content }
        }).done(function(result) {
            wrapper.empty().append(result);
            disableIframes(wrapper);
            refreshSort();
        });
    }
}

function validateContent(widget) {
    if(widget.attr('data-widget') == 'quote') {
        return JSON.stringify({
            widget: "quote",
            quote: widget.find("textarea[name='quote']").val(),
            author: widget.find("input[name='author']").val()
        });
    } else if(widget.attr('data-widget') == 'carousel') {
        ImageCarouselWidget.saveCropping();
        return ImageCarouselWidget.validateContent();

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
        return JSON.stringify({
            widget: "articles",
            title: title,
            tag_link: tag_link,
            tags: tags,
            count: count
        });
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
        return JSON.stringify({
            widget: "blog",
            count: count,
            category : category
        });
    } else if(widget.attr('data-widget') == 'embed') {
        var code = widget.find("textarea[name='code']").val();
        if(code == '') {
            alert("Du må jo legge inn koden du vil bruke først! Hvis du ikke vil bruke widgeten likevel, trykk på 'Slett widget'-knappen.");
            return false;
        }
        return JSON.stringify({
            widget: "embed",
            code: code
        });
    } else if(widget.attr('data-widget') == 'fact') {
        var content = widget.find("div.content").html();
        return JSON.stringify({
            widget: "fact",
            content: content
        });
    }
}

function openWidgetDialog(type, parentWidth){
    if(type == 'carousel') {
        ImageCarouselWidget.listImages(parentWidth);
    }
}

function editWidget() {
    widgetBeingEdited = $(this);
    var widget = JSON.parse($(this).attr('data-json'));
    $("div.widget-editor[data-widget='" + widget.widget + "']").modal();
    if(widget.widget == 'quote') {
        $("div.widget-editor[data-widget='quote'] textarea[name='quote']").val(widget.quote);
        $("div.widget-editor[data-widget='quote'] input[name='author']").val(widget.author);
    } else if(widget.widget == 'articles') {
        var articles = $("div.widget-editor[data-widget='articles']");
        articles.find("input[name='title']").val(widget.title);
        articles.find("input[name='count']").val(widget.count);
        if(widget.tag_link == null) {
            articles.find("input[name='set-tag-link']").removeAttr('checked');
            articles.find("input[name='tag-link']").attr('disabled', true).val("");
        }
        article_widget_tagger.tags = widget.tags;
        var box = articles.find("div.tag-box");
        box.empty();
        for(var i=0; i<widget.tags.length; i++) {
            var tag = $('<div class="tag"><a href="javascript:undefined"><img src="/static/img/so/close-default.png"></a> ' + widget.tags[i] + '</div>');
            box.append(tag);
        }
        if(widget.tags.length > 0) {
            articles.find("input[name='enable-tags']").attr('checked', true);
            articles.find("input[name='tags']").removeAttr('disabled');
        } else {
            articles.find("input[name='enable-tags']").removeAttr('checked');
            articles.find("input[name='tags']").attr('disabled', true);
        }
    } else if(widget.widget == 'blog') {
        $("div.widget-editor[data-widget='blog'] input[name='count']").val(widget.count);
        $("div.widget-editor[data-widget='blog'] select[name='category']").val(widget.category);
    } else if(widget.widget == 'embed') {
        $("div.widget-editor[data-widget='embed'] textarea[name='code']").text(widget.code);
    }else if(widget.widget == 'carousel') {
        ImageCarouselWidget.listImages();
    } else if(widget.widget == 'fact') {
        $("div.widget-editor[data-widget='fact'] div.content").html(widget.content);
    }
}
