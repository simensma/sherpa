(function(FactWidgetEditor, $, undefined ) {

    var widget_editor; // Gets set in the preparations below

    /* New widget */

    $(document).on('widget.new.fact', function() {
        widget_editor.modal();
    });

    /* Editing existing widget */

    $(document).on('widget.edit', 'div.widget.fact', function() {
        widgetBeingEdited = $(this);
        widget_editor.modal();
        var widget = JSON.parse($(this).attr('data-json'));

        widget_editor.find("div.content").html(widget.content);
    });

    /* Document preparations */

    $(document).ready(function() {

        widget_editor = $("div.widget-editor[data-widget='fact']");

        /* Saving */
        widget_editor.find("button.save").click(function() {
            var content = widget_editor.find("div.content").html();
            saveWidget({
                widget: "fact",
                content: content
            });
            widget_editor.modal('hide');
        });

    });

}(window.FactWidgetEditor = window.FactWidgetEditor || {}, jQuery ));
