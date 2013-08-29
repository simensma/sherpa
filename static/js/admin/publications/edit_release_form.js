$(document).ready(function() {

    var form = $("form.edit-release");
    var input_cover_photo = form.find("input[name='cover_photo']");
    var cover_photo_image = form.find("img.cover_photo");
    var cover_photo_ajaxloader = form.find("div.control-group.cover_photo img.ajaxloader");

    input_cover_photo.change(function() {
        cover_photo_image.off('load.archive-image');
        cover_photo_image.on('load.archive-image', function() {
            cover_photo_ajaxloader.hide();
            cover_photo_image.show();
        });
        cover_photo_image.hide();
        cover_photo_ajaxloader.show();
        cover_photo_image.attr('src', $(this).val());
    });

    form.find("div.control-group.cover_photo a.pick-from-image-archive").click(function() {
        ImageArchivePicker.pick(function(url, description, photographer) {
            input_cover_photo.val(url);
            input_cover_photo.change();
        });
    });

    form.find("div.control-group.cover_photo a.upload-new-image").click(function() {
        ImageUploadDialog.open(function(url, description, photographer) {
            input_cover_photo.val(url);
            input_cover_photo.change();
        });
    });

    form.find("div.pub_date-wrapper").datepicker({
        format: 'dd.mm.yyyy',
        weekStart: 1,
        autoclose: true,
        language: 'nb',
        forceParse: false
    });

    TagDisplay.enable({
        targetInput: form.find("div.control-group.tags input[name='tags-serialized']"),
        tagBox: form.find("div.tag-box"),
        pickerInput: form.find("input[name='tags']")
    });

    // Send the tags with the tags-serialized input upon submit
    form.submit(function() {
       TagDisplay.collect();
    });

});
