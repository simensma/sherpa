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
            type: 'POST'
        });
        $(document).on('ajaxSend', function(event, xhr) {
            xhr.setRequestHeader("X-CSRFToken", $("input[name='csrfmiddlewaretoken']").val());
        });
    }

    /* For any close button, close its parent alert */
    $(document).on('click', 'a.close', function() { $(this).parent().hide(); });

    /* Add class to external links */
    $("a:not(.btn)").each(function() {
        if($(this).children().length > 0) {
            // Don't add to anchors with more than text nodes as children
            return $(this);
        }
        if($(this).parents("article[data-id]").length > 0) {
            // Don't add to anchors when editing article
            return $(this);
        }
        if($(this).attr('href') === undefined || $(this).attr('href') === false) {
            return $(this);
        }
        var hostname = $(this).get(0).hostname;
        if(hostname != '' && hostname != location.hostname) {
            $(this).addClass('external');
        }
    });

    /* Enable any popovers */
    $("*[data-popover]").popover();


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

// The escape key seems to only work for IE, not Opera or Firefox, so simulate
// the modal close upon escape keypress.
$(document).on('keypress', 'body', function(e) {
    if(e.which == 0) {
        $(".modal").modal('hide');
    }
});
