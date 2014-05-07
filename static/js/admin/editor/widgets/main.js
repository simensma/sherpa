/* Editing widgets */

function saveWidget(content, editor_callback) {
    var editor = $("div.cms-editor");
    var article = editor.find("article");
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

}
