(function(BlogWidgetEditor, $, undefined ) {

    var widget_editor; // Gets set in the preparations below

    /* Editing existing widget */

    $(document).on('widget.edit', 'div.widget.blog', function() {
        widgetBeingEdited = $(this);
        widget_editor.modal();
        var widget = JSON.parse($(this).attr('data-json'));

        widget_editor.find("input[name='count']").val(widget.count);
        widget_editor.find("select[name='category']").val(widget.category);
    });

    /* Document preparations */

    $(document).ready(function() {

        widget_editor = $("div.widget-editor[data-widget='blog']");

    });

}(window.BlogWidgetEditor = window.BlogWidgetEditor || {}, jQuery ));
