(function(EmbedWidgetEditor, $, undefined ) {

    var widget_editor; // Gets set in the preparations below

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

    });

}(window.EmbedWidgetEditor = window.EmbedWidgetEditor || {}, jQuery ));
