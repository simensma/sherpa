(function(BlogWidgetEditor, $, undefined ) {

    var widget_editor; // Gets set in the preparations below

    /* New widget */

    $(document).on('widget.new.blog', function() {
        widget_editor.modal();
    });

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

            saveWidget({
                widget: "blog",
                count: count,
                category : category
            });
            widget_editor.modal('hide');
        });

    });

}(window.BlogWidgetEditor = window.BlogWidgetEditor || {}, jQuery ));
