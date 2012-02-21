$(document).ready(function() {

    /* For any close button, close its parent alert */
    $("a.close").click(function() { $(this).parent().hide(); });

    /* Scale article image sidebars according to the image width */
    $("article .image-right").each(function() {
        $(this).width($(this).children("img").width());
    });

});
