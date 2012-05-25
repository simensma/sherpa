/* Editing widgets */
$(document).ready(function() {

    /* This file can be heavily refactored */

    // Save quote-widget
    $("div.dialog.widget-edit.quote button.save").click(function() {
        var content = JSON.stringify({
            widget: "quote",
            quote: $("div.dialog.widget-edit.quote textarea[name='quote']").val(),
            author: $("div.dialog.widget-edit.quote input[name='author']").val()
        });
        if(widgetBeingEdited !== undefined) {
            $("div.dialog.widget-edit.quote").dialog('close');
            enableOverlay();
            saveWidget(widgetBeingEdited, content);
        } else {
            $(this).parents(".dialog").dialog('close');
            addContent(widgetPosition.prev, widgetPosition.parent, widgetPosition.column,
                widgetPosition.order, content, 'widget', widgetAdded);
        }
    });

    // Save articles-widget
    $("div.dialog.widget-edit.articles button.save").click(function() {
        var count = $("div.dialog.widget-edit.articles input[name='count']").val();
        if(isNaN(Number(count))) {
            alert("Du må angi et tall for antall artikler som skal vises!");
            return $(this);
        } else if(count < 1) {
            alert("Du må vise minst én artikkel!");
            return $(this);
        }
        var content = JSON.stringify({
            widget: "articles",
            count: count
        });
        if(widgetBeingEdited !== undefined) {
            $("div.dialog.widget-edit.articles").dialog('close');
            enableOverlay();
            saveWidget(widgetBeingEdited, content);
        } else {
            $(this).parents(".dialog").dialog('close');
            addContent(widgetPosition.prev, widgetPosition.parent, widgetPosition.column,
                widgetPosition.order, content, 'widget', widgetAdded);
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

function widgetAdded(wrapper) {
    refreshSort();
    removeEmpties();
    setEmpties();
}

function saveWidget(widget, content) {
    $.ajax({
        url: '/sherpa/cms/widget/oppdater/' + widget.attr('data-id') + '/',
        type: 'POST',
        data: 'content=' + encodeURIComponent(content)
    }).done(function(result) {
        result = JSON.parse(result);
        widget.contents().remove();
        widget.append(result.content);
        widget.attr('data-json', result.json);
    }).always(function() {
        disableOverlay();
    });
}

function editWidget() {
    widgetBeingEdited = $(this);
    var widget = JSON.parse($(this).attr('data-json'));
    if(widget.widget == 'quote') {
        $("div.dialog.widget-edit.quote textarea[name='quote']").val(widget.quote);
        $("div.dialog.widget-edit.quote input[name='author']").val(widget.author);
        $("div.dialog.widget-edit.quote").dialog('open');
    } else if(widget.widget == 'articles') {
        $("div.dialog.widget-edit.articles input[name='count']").val(widget.count);
        $("div.dialog.widget-edit.articles").dialog('open');
    }
}
