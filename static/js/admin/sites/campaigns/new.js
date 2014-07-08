$(function() {

    var wrapper = $("div.new-campaign");

    wrapper.find("button.pick-from-image-archive").click(function() {
        ImageArchivePicker.pick(function(url, description, photographer) {
            // TBD
        });
    });

    wrapper.find("button.upload-new-image").click(function() {
        ImageUploadDialog.open(function(url, description, photographer) {
            // TBD
        });
    });

});
