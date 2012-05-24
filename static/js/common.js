/**
 * Common for admin-ui and main site
 */
$(document).ready(function() {

    /* Enable all dialogs */
    $(".dialog").enableDialog();
    $(".dialog-button").enableDialogButton();

    /* Include CSRF-token when applicable in AJAX requests */
    if($("input[name='csrfmiddlewaretoken']").length > 0) {
        $.ajaxSetup({
            beforeSend: function(xhr, settings) {
                xhr.setRequestHeader("X-CSRFToken", $("input[name='csrfmiddlewaretoken']").val());
            }
        });
    }

    /* For any close button, close its parent alert */
    $("a.close").click(function() { $(this).parent().hide(); });

    /* Add class to external links */
    $("a").each(function() {
        if($(this).children().length > 0) {
            // Don't add to anchors with more than text nodes as children
            return $(this);
        }
        var hostname = $(this).get(0).hostname;
        if(hostname != '' && hostname != location.hostname) {
            $(this).addClass('external');
        }
    });

});

$.fn.enableDialog = function() {
    return this.each(function() {
        $(this).dialog({
            title: $(this).attr('data-title'),
            modal: true,
            autoOpen: false,
            width: $(this).attr('data-width')
        }).hide();
    });
}

$.fn.enableDialogButton = function() {
    return this.each(function() {
        $(this).click(function(event) {
            $($(this).attr('data-dialog')).dialog('open');
        });
    });
}
