$(function() {

    $("button.upload-image").click(function() {
        ImageUploadDialog.open(function(url, description, photographer) {
            // TBD
        });
    });

});
