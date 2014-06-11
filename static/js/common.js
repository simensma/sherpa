/**
 * Common for admin-ui and main site
 */
$(function() {

    /* Include CSRF-token when applicable in AJAX requests */
    if($("input[name='csrfmiddlewaretoken']").length > 0) {
        $.ajaxSetup({
            type: 'POST',
            cache: false
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
        if($(this).parents("article").length > 0 && $("div.editor-header").length > 0) {
            // Don't add to anchors when editing article
            return $(this);
        }
        if($(this).attr('href') === undefined || $(this).attr('href') === false) {
            return $(this);
        }
        var hostname = $(this).get(0).hostname;
        if(hostname !== '' && hostname != location.hostname) {
            $(this).addClass('external');
        }
    });

    /* Enable any popovers */
    $("*[data-popover]").popover({
        container: 'body'
    });

    /* Enable any tooltips */
    $("*[data-tooltip]").tooltip();

    /* Tags use data-href for links */
    $("div.tag-box div.tag[data-href]").click(function() {
        window.location = $(this).attr('data-href');
    });

    /* Enable self-declared chosen selects */
    $("select[data-chosen]").chosen();

    /* Sliders */
    $("div.slider").each(function() {
        var content = $(this).find("div.slider-content");
        var bar = $(this).find("a.slider-bar");

        bar.click(function() {
            content.slideToggle();
            $(this).find("span.text,div.button").toggle();
        });
    });

});

// The escape key seems to only work for IE, not Opera or Firefox, so simulate
// the modal close upon escape keypress.
$(document).on('keypress', 'body', function(e) {
    if(e.which === 27) {
        $(".modal").modal('hide');
    }
});

// Simple framebusting; mainly for facebook
if(top != self) {
    top.location.replace(document.location);
}

/* Toggling a tab-pane outside from the actual tab links */
$(document).on("click", "*[data-toggle-tab]", function() {
    $("ul.nav-tabs a[href='#" + $(this).attr('data-toggle-tab') + "']").tab('show');
});
