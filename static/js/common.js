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
    $("a:not(.btn)").each(function() {
        if($(this).children().length > 0) {
            // Don't add to anchors with more than text nodes as children
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

$(window).load(function() {
    /* Shrink image-description-width to image width (for those cases where image isn't 100%) */
    $("article div.content.image").each(function() {
        var desc = $(this).find("div.img-desc");
        if(desc.length > 0) {
            var strip = Number(desc.css('padding-left').replace('px', '')) + Number(desc.css('padding-right').replace('px', ''));
            desc.width($(this).find("img").innerWidth() - strip);
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
