$(document).ready(function() {
    var form = $("form.edit-publication");
    var input_logo = form.find("input[name='logo']");
    var logo_image = form.find("img.logo");
    var association_select = form.find("select[name='association']");
    var access_association_name = form.find("div.control-group.access span.association-name");

    input_logo.change(function() {
        logo_image.attr('src', $(this).val());
    });

    association_select.change(function() {
        var name = window.association_main_mappings[$(this).find("option:selected").val()];
        access_association_name.text(name);
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
