$(document).ready(function() {

    var content_wrappers = $("div.publications div.content-wrapper");

    content_wrappers.hover(function() {
        $(this).find('.hover-content').fadeIn(200);
    }, function() {
        $(this).find('.hover-content').fadeOut(200);
    });

    $(window).load(function() {
        // Set the hover-content dimensions after images have loaded
        content_wrappers.each(function() {
            var content = $(this).find("div.hover-content");
            var img = $(this).find("img");
            var contentWidthPadding = content.outerWidth() - content.width();
            var contentHeightPadding = content.outerHeight() - content.height();
            content.offset(img.offset());
            content.width(img.width() - contentWidthPadding);
            content.height(img.height() - contentHeightPadding);
        });
    });

});
