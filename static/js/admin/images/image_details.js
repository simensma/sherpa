$(document).ready(function() {
    var exif = false;
    $("#image-display div.exif").hide();
    $("#image-display a.toggle-exif").click(function() {
        if(exif) {
            $(this).text("Vis...");
            $("#image-display div.exif").hide();
            exif = false;
        } else {
            $(this).text("Skjul...");
            $("#image-display div.exif").show();
            exif = true;
        }
    });
});
