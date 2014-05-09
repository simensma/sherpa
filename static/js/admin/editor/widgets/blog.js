(function(BlogWidgetEditor, $, undefined ) {

    var widget_editor; // Gets set in the preparations below
    var editor_callback; // Sent with the trigger from the editor

    /* New widget */

    $(document).on('widget.new.blog', function(e, _editor_callback) {
        editor_callback = _editor_callback;
        widget_editor.modal();
    });

    /* Editing existing widget */

    $(document).on('widget.edit', 'div.widget.blog', function(e, widget_content, _editor_callback) {
        editor_callback = _editor_callback;
        widget_editor.modal();

        widget_editor.find("input[name='count']").val(widget_content.count);
        widget_editor.find("select[name='category']").val(widget_content.category);
    });

    /* Document preparations */

    $(document).ready(function() {

        widget_editor = $("div.widget-editor[data-widget='blog']");

        /* Saving */
        widget_editor.find("button.save").click(function() {
            var count = widget_editor.find("input[name='count']").val();
            var category = widget_editor.find("select[name='category']").val();

            if(isNaN(Number(count))) {
                alert("Du må angi et tall for antall blogginnlegg som skal vises!");
                return $(this);
            } else if(count < 1) {
                alert("Du må vise minst ett blogginnlegg!");
                return $(this);
            }

            WidgetEditor.saveWidget({
                widget: "blog",
                count: count,
                category : category
            }, editor_callback);
            widget_editor.modal('hide');
        });

    });

}(window.BlogWidgetEditor = window.BlogWidgetEditor || {}, jQuery ));
