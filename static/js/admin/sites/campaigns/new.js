$(function() {

    var wrapper = $("div.new-campaign");
    var section_progress = wrapper.find(".section-progress");
    var step2 = wrapper.find("div.step2");

    wrapper.find("button.pick-from-image-archive").click(function() {
        ImageArchivePicker.pick(function(url, description, photographer) {
            enableStep2();
        });
    });

    wrapper.find("button.upload-new-image").click(function() {
        ImageUploadDialog.open(function(url, description, photographer) {
            enableStep2();
        });
    });

    function enableStep2() {
        section_progress.find("li").first().removeClass('active');
        section_progress.find("li").last().addClass('active');
        step2.show();
    }

});
