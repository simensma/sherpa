(function(FactWidgetEditor, $, undefined ) {

    var widget_editor; // Gets set in the preparations below
    var editor_callback; // Sent with the trigger from the editor

    /* New widget */

    $(document).on('widget.new.fact', function(e, _editor_callback) {
        editor_callback = _editor_callback;
        widget_editor.modal();
    });

    /* Editing existing widget */

    $(document).on('widget.edit', 'div.widget.fact', function(e, widget_content, _editor_callback) {
        editor_callback = _editor_callback;
        widget_editor.modal();

        widget_editor.find("div.content").html(widget_content.content);
    });

    /* Document preparations */

    $(document).ready(function() {

        widget_editor = $("div.widget-editor[data-widget='fact']");

        /* Saving */
        widget_editor.find("button.save").click(function() {
            var content = widget_editor.find("div.content").html();
            WidgetEditor.saveWidget({
                widget: "fact",
                content: content
            }, editor_callback);
            widget_editor.modal('hide');
        });

    });

}(window.FactWidgetEditor = window.FactWidgetEditor || {}, jQuery ));
