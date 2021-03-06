$(function() {

    var form = $("form.edit-release");
    var input_cover_photo = form.find("input[name='cover_photo']");
    var cover_photo_image = form.find("img.cover_photo");
    var cover_photo_ajaxloader = form.find("div.form-group.cover_photo img.ajaxloader");

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

    form.find("div.form-group.cover_photo a.pick-from-image-archive").click(function() {
        ImageArchivePicker.pick(function(image) {
            input_cover_photo.val(image.url);
            input_cover_photo.change();
        });
    });

    form.find("div.form-group.cover_photo a.upload-new-image").click(function() {
        ImageUploadDialog.open(function(image) {
            input_cover_photo.val(image.url);
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

    Select2Tagger({$input: form.find('div.form-group.tags input[name="tags"]')});
});
