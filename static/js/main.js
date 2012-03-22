$(document).ready(function() {

    /* Scale article image sidebars according to the image width */
    $("article .image-right").each(function() {
        $(this).width($(this).children("img").width());
    });

});
