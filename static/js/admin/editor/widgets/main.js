/* Editing widgets */
$(document).ready(function() {

    // Remove any widget
    $("div.widget-editor button.remove").click(function() {
        $(this).parents(".widget-editor").modal('hide');
        if(typeof widgetBeingEdited !== 'undefined'){
            removeContent(widgetBeingEdited);
        }
    });

    $("div.add-widget div.widget-thumbnail").tooltip();

});

function saveWidget(widget, content) {
    var rendring_message = '<img src="/static/img/ajax-loader-small.gif" alt="Laster..."> <em>Rendrer widget...</em>';
    var rendring_failed = '<p class="widget-rendring-failed">Klarte ikke å rendre widgeten! Er du sikker på at du har tilgang til internett?<br>Klikk her og velg lagre på nytt for å prøve å rendre igjen.</p>'
    var content_json = JSON.stringify(content);
    var article = $("article");
    if(widget !== undefined) {
        widget.empty().append(rendring_message);
        widget.attr('data-json', content_json);
        $.ajaxQueue({
            url: article.attr('data-render-widget-url'),
            data: { content: content_json }
        }).fail(function(result) {
            widget.empty().append(rendring_failed);
        }).done(function(result) {
            widget.empty().hide().append(result);
            widget.slideDown();
            disableIframes(widget);
        });
    } else {
        var widget = $('<div class="content widget ' + content.widget + '"></div>');
        widget.append(rendring_message);
        widget.attr('data-json', content_json);
        if(widgetPosition.prev.length == 0) {
            widgetPosition.parent.prepend(widget);
        } else {
            widgetPosition.prev.after(widget);
        }
        removeEmpties();
        setEmpties();
        $.ajaxQueue({
            url: article.attr('data-render-widget-url'),
            data: { content: content_json }
        }).fail(function(result) {
            widget.empty().append(rendring_failed);
        }).done(function(result) {
            widget.empty().hide().append(result);
            widget.slideDown();
            disableIframes(widget);
        });
    }
}
