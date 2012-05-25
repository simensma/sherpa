/* Editing widgets */
$(document).ready(function() {

    // Save any widget
    $("div.dialog.widget-edit button.save").click(function() {
        var content = validateContent($(this).parents("div.dialog.widget-edit"));
        if(content === false) {
            return $(this);
        }
        $("div.dialog.widget-edit").dialog('close');
        if(widgetBeingEdited !== undefined) {
            enableOverlay();
            $.ajax({
                url: '/sherpa/cms/widget/oppdater/' + widgetBeingEdited.attr('data-id') + '/',
                type: 'POST',
                data: 'content=' + encodeURIComponent(content)
            }).done(function(result) {
                result = JSON.parse(result);
                widgetBeingEdited.contents().remove();
                widgetBeingEdited.append(result.content);
                widgetBeingEdited.attr('data-json', result.json);
                disableIframes(widgetBeingEdited);
            }).always(function() {
                disableOverlay();
            });
        } else {
            addContent(widgetPosition.prev, widgetPosition.parent, widgetPosition.column,
                widgetPosition.order, content, 'widget', function(wrapper) {
                    refreshSort();
                    removeEmpties();
                    setEmpties();
            });
        }
    });

    // Remove any widget
    $("div.dialog.widget-edit button.remove").click(function() {
        $(this).parents(".dialog").dialog('close');
        $.ajax({
            url: '/sherpa/cms/innhold/slett/' + encodeURIComponent(widgetBeingEdited.attr('data-id')) + '/',
            type: 'POST'
        }).done(function(result) {
            if(widgetBeingEdited.siblings().length == 0) {
                setEmpty(widgetBeingEdited.parent());
            }
            widgetBeingEdited.remove();
        }).fail(function(result) {
            // Todo
        }).always(function(result) {
            refreshSort();
            disableOverlay();
        });
    });

});

function validateContent(widget) {
    if(widget.attr('data-widget') == 'quote') {
        return JSON.stringify({
            widget: "quote",
            quote: widget.find("textarea[name='quote']").val(),
            author: widget.find("input[name='author']").val()
        });
    } else if(widget.attr('data-widget') == 'articles') {
        var count = widget.find("input[name='count']").val();
        if(isNaN(Number(count))) {
            alert("Du må angi et tall for antall artikler som skal vises!");
            return false;
        } else if(count < 1) {
            alert("Du må vise minst én artikkel!");
            return false;
        }
        return JSON.stringify({
            widget: "articles",
            count: count
        });
    } else if(widget.attr('data-widget') == 'blog') {
        var count = widget.find("input[name='count']").val();
        if(isNaN(Number(count))) {
            alert("Du må angi et tall for antall blogginnlegg som skal vises!");
            return false;
        } else if(count < 1) {
            alert("Du må vise minst ett blogginnlegg!");
            return false;
        }
        return JSON.stringify({
            widget: "blog",
            count: count
        });
    }
}

function editWidget() {
    widgetBeingEdited = $(this);
    var widget = JSON.parse($(this).attr('data-json'));
    if(widget.widget == 'quote') {
        $("div.dialog.widget-edit[data-widget='quote'] textarea[name='quote']").val(widget.quote);
        $("div.dialog.widget-edit[data-widget='quote'] input[name='author']").val(widget.author);
        $("div.dialog.widget-edit[data-widget='quote']").dialog('open');
    } else if(widget.widget == 'articles') {
        $("div.dialog.widget-edit[data-widget='articles'] input[name='count']").val(widget.count);
        $("div.dialog.widget-edit[data-widget='articles']").dialog('open');
    } else if(widget.widget == 'blog') {
        $("div.dialog.widget-edit[data-widget='blog'] input[name='count']").val(widget.count);
        $("div.dialog.widget-edit[data-widget='blog']").dialog('open');
    }
}
