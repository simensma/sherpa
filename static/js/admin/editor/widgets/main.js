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

function saveWidget(content) {
    var rendring_message = '<img src="/static/img/ajax-loader-small.gif" alt="Laster..."> <em>Rendrer widget...</em>';
    var content_json = JSON.stringify(content);
    if(typeof widgetBeingEdited !== 'undefined') {
        widgetBeingEdited.empty().append(rendring_message);
        widgetBeingEdited.attr('data-json', content_json);
        $.ajaxQueue({
            url: '/sherpa/cms/widget/',
            data: { content: content_json }
        }).done(function(result) {
            widgetBeingEdited.empty().append(result);
            disableIframes(widgetBeingEdited);
        });
    } else {
        var wrapper = $('<div class="content widget ' + content.widget + '"></div>');
        wrapper.append(rendring_message);
        wrapper.attr('data-json', content_json);
        if(widgetPosition.prev.length == 0) {
            widgetPosition.parent.prepend(wrapper);
        } else {
            widgetPosition.prev.after(wrapper);
        }
        removeEmpties();
        setEmpties();
        $.ajaxQueue({
            url: '/sherpa/cms/widget/',
            data: { content: content_json }
        }).done(function(result) {
            wrapper.empty().append(result);
            disableIframes(wrapper);
            refreshSort();
        });
    }
}
