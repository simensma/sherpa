(function(EmbedWidgetEditor, $, undefined ) {

    var widget_editor; // Gets set in the preparations below
    var editor_callback; // Sent with the trigger from the editor

    /* New widget */

    $(document).on('widget.new.embed', function(e, _editor_callback) {
        editor_callback = _editor_callback;
        widget_editor.modal();
    });

    /* Editing existing widget */

    $(document).on('widget.edit', 'div.widget.embed', function(e, widget_content, _editor_callback) {
        editor_callback = _editor_callback;
        widget_editor.modal();

        widget_editor.find("textarea[name='code']").text(widget_content.code);
    });

    /* Document preparations */

    $(document).ready(function() {

        widget_editor = $("div.widget-editor[data-widget='embed']");

        /* Saving */
        widget_editor.find("button.save").click(function() {
            var code = widget_editor.find("textarea[name='code']").val();
            if(code == '') {
                alert("Du må jo legge inn koden du vil bruke først! Hvis du ikke vil bruke widgeten likevel, lukk vinduet med krysset oppe til høyre.");
                return $(this);
            }
            saveWidget({
                widget: "embed",
                code: code
            }, editor_callback);
            widget_editor.modal('hide');
        });

    });

}(window.EmbedWidgetEditor = window.EmbedWidgetEditor || {}, jQuery ));
