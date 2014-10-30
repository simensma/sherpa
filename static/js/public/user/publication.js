$(function() {

    var content_wrappers = $("div.publications div.content-wrapper");

    content_wrappers.hover(function() {
        $(this).find('.hover-content').fadeIn(200);
    }, function() {
        $(this).find('.hover-content').fadeOut(200);
    });

});
