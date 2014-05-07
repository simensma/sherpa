(function(QuoteWidgetEditor, $, undefined ) {

    var widget_editor; // Gets set in the preparations below
    var editor_callback; // Sent with the trigger from the editor


    /* New widget */

    $(document).on('widget.new.quote', function(e, _editor_callback) {
        editor_callback = _editor_callback;
        widget_editor.modal();
    });

    /* Editing existing widget */

    $(document).on('widget.edit', 'div.widget.quote', function(e, widget_content, _editor_callback) {
        editor_callback = _editor_callback;
        widget_editor.modal();

        widget_editor.find("textarea[name='quote']").val(widget_content.quote);
        widget_editor.find("input[name='author']").val(widget_content.author);
    });

    /* Document preparations */

    $(document).ready(function() {

        widget_editor = $("div.widget-editor[data-widget='quote']");

        /* Saving */
        widget_editor.find("button.save").click(function() {
            saveWidget({
                widget: "quote",
                quote: widget_editor.find("textarea[name='quote']").val(),
                author: widget_editor.find("input[name='author']").val()
            }, editor_callback);
            widget_editor.modal('hide');
        });

    });

}(window.QuoteWidgetEditor = window.QuoteWidgetEditor || {}, jQuery ));
