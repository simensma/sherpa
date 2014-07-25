$(function() {

    // Add cropping to cropped images
    $("div.content.image[data-crop]").each(function() {
        ImageCropper.cropImage(
            JSON.parse($(this).attr('data-crop')),
            $(this).find('img'),
            $(this),
            $(this).parent().width()
        );
    });

});
