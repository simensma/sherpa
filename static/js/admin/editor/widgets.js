$(document).ready(function() {

    /* Editing widgets */

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

    function editWidget(widget) {
        if(widget.widget == 'quote') {
            $("div.dialog.widget-edit.quote textarea[name='quote']").val(widget.quote);
            $("div.dialog.widget-edit.quote input[name='author']").val(widget.author);
            $("div.dialog.widget-edit.quote").dialog('open');
        }
    }

});
