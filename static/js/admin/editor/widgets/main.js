/* Editing widgets */

(function(WidgetEditor, $, undefined ) {

    var editor;
    var article;
    var editor_callback;

    $(function() {
        editor = $("div.cms-editor");
        article = editor.find("article");
    });

    WidgetEditor.listen = function(opts) {
        // Can't use the 'editor' element for lookup; listen may be called before the ready-function above runs
        var widget_editor = $("div.cms-editor div.widget-editor[data-widget='" + opts.widget_name + "']");

        if(opts.init !== undefined) {
            opts.init(widget_editor);
        }

        $(document).on('widget.new.' + opts.widget_name, function(e, _editor_callback) {
            editor_callback = _editor_callback;
            widget_editor.modal();
            if(opts.onNew !== undefined) {
                opts.onNew(widget_editor);
            }
        });

        $(document).on('widget.edit', 'div.widget.' + opts.widget_name, function(e, widget_content, _editor_callback) {
            editor_callback = _editor_callback;
            widget_editor.modal();
            if(opts.onEdit !== undefined) {
                opts.onEdit(widget_editor, widget_content);
            }
        });

        widget_editor.find("button.save").click(function() {
            if(opts.onSave(widget_editor)) {
                widget_editor.modal('hide');
            }
        });
    };

    WidgetEditor.saveWidget = function(content) {
        var rendering_failed = editor.find("div.insertion-templates p.widget-rendering-failed").clone();
        var content_json = JSON.stringify(content);

        var widget = editor.find("div.insertion-templates div.content.widget").clone();
        widget.addClass(content.widget);
        widget.attr('data-json', content_json);

        // Insert the new widget with its rendering message
        editor_callback(widget);

        // Now attempt the render, and edit the object in-place
        $.ajaxQueue({
            url: article.attr('data-render-widget-url'),
            data: { content: content_json }
        }).fail(function(result) {
            widget.empty().append(rendering_failed);
        }).done(function(result) {
            widget.empty().hide().append(result);
            widget.slideDown();
            disableIframes(widget);
        });
    };

}(window.WidgetEditor = window.WidgetEditor || {}, jQuery ));
