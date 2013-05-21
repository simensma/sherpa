$(document).ready(function() {
    $("a.show-exif").click(function() {
        $(this).hide();
        $(this).siblings("div.exif").show();
    });
});
