$(function() {

    var wrapper = $("div.new-campaign");

    wrapper.find("button.upload-image").click(function() {
        ImageUploadDialog.open(function(url, description, photographer) {
            // TBD
        });
    });

});
