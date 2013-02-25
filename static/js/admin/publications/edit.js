$(document).ready(function() {
    var form = $("form.edit-publication");
    var input_logo = form.find("input[name='logo']");
    var logo_image = form.find("img.logo");

    input_logo.change(function() {
        logo_image.attr('src', $(this).val());
    });

    form.find("div.control-group.logo a.pick-from-image-archive").click(function() {
        ImageArchivePicker.pick(function(url, description, photographer) {
            input_logo.val(url);
            input_logo.change();
        });
    });

    form.find("div.control-group.logo a.upload-new-image").click(function() {
        ImageUploadDialog.open(function(url, description, photographer) {
            input_logo.val(url);
            input_logo.change();
        });
    });
});
