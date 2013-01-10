(function(EmbedWidgetEditor, $, undefined ) {

    var widget_editor; // Gets set in the preparations below

    /* New widget */

    $(document).on('widget.new.embed', function() {
        widget_editor.modal();
    });

    /* Editing existing widget */

    $(document).on('widget.edit', 'div.widget.embed', function() {
        widgetBeingEdited = $(this);
        widget_editor.modal();
        var widget = JSON.parse($(this).attr('data-json'));

        widget_editor.find("textarea[name='code']").text(widget.code);
    });

    /* Document preparations */

    $(document).ready(function() {

        widget_editor = $("div.widget-editor[data-widget='embed']");

        /* Saving */
        widget_editor.find("button.save").click(function() {
            var code = widget_editor.find("textarea[name='code']").val();
            if(code == '') {
                alert("Du må jo legge inn koden du vil bruke først! Hvis du ikke vil bruke widgeten likevel, trykk på 'Slett widget'-knappen.");
                return $(this);
            }
            saveWidget(widgetBeingEdited, {
                widget: "embed",
                code: code
            });
            widget_editor.modal('hide');
        });

    });

}(window.EmbedWidgetEditor = window.EmbedWidgetEditor || {}, jQuery ));
