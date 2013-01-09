(function(QuoteWidgetEditor, $, undefined ) {

    var widget_editor; // Gets set in the preparations below

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

    });

}(window.QuoteWidgetEditor = window.QuoteWidgetEditor || {}, jQuery ));
