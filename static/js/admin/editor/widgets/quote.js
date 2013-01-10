(function(QuoteWidgetEditor, $, undefined ) {

    var widget_editor; // Gets set in the preparations below


    /* New widget */

    $(document).on('widget.new.quote', function() {
        widget_editor.modal();
    });

    /* Editing existing widget */

    $(document).on('widget.edit', 'div.widget.quote', function() {
        widgetBeingEdited = $(this);
        widget_editor.modal();
        var widget = JSON.parse($(this).attr('data-json'));

        widget_editor.find("textarea[name='quote']").val(widget.quote);
        widget_editor.find("input[name='author']").val(widget.author);
    });

    /* Document preparations */

    $(document).ready(function() {

        widget_editor = $("div.widget-editor[data-widget='quote']");

        /* Saving */
        widget_editor.find("button.save").click(function() {
            saveWidget(widgetBeingEdited, {
                widget: "quote",
                quote: widget_editor.find("textarea[name='quote']").val(),
                author: widget_editor.find("input[name='author']").val()
            });
            widget_editor.modal('hide');
        });

    });

}(window.QuoteWidgetEditor = window.QuoteWidgetEditor || {}, jQuery ));
