(function(ImageDialog, $, undefined ) {

    var image_picked_callback; // Called when an image is picked in the dialog
    var image_removed_callback; // Called when an image is removed, from the dialog
    var image_dialog;

    $(function() {

        image_dialog = $("div.cms-editor div.change-image");

        image_dialog.find("button.choose-image").click(function() {
            ImageArchivePicker.pick(insertImageDetails);
        });

        image_dialog.find("button.upload-image").click(function() {
            ImageUploadDialog.open(insertImageDetails);
        });

        function insertImageDetails(url, description, photographer) {
            image_dialog.find("input[name='src']").val(ImageUtils.removeImageSizeFromUrl(url));
            image_dialog.find("input[name='description']").val(description);
            image_dialog.find("input[name='photographer']").val(photographer);
        }

        image_dialog.find("button.insert-image").click(function() {
            var src = image_dialog.find("input[name='src']").val().trim();
            if(src === "") {
                alert(image_dialog.attr('data-missing-url-warning'));
                return;
            }

            var anchor = image_dialog.find("input[name='anchor']").val().trim();
            if(anchor.length !== 0 && !anchor.match(/^https?:\/\//)) {
                anchor = "http://" + anchor;
            }

            var description = image_dialog.find("input[name='description']").val().trim();
            var photographer = image_dialog.find("input[name='photographer']").val().trim();
            image_picked_callback(src, anchor, description, photographer);
            image_dialog.modal('hide');
        });

        var photographer = image_dialog.find("input[name='photographer']");
        photographer.typeahead({
            minLength: 3,
            remote: photographer.attr('data-photographers-url') + '?q=%QUERY'
        });
    });

    ImageDialog.openImageDialog = function(opts) {
        image_picked_callback = opts.save;
        image_removed_callback = opts.remove;

        image_dialog.find("input[name='src']").val(ImageUtils.removeImageSizeFromUrl(opts.image.attr("src")));
        image_dialog.find("input[name='anchor']").val(opts.anchor);
        image_dialog.find("input[name='description']").val(opts.description);
        image_dialog.find("input[name='photographer']").val(opts.photographer);
        image_dialog.modal();
    };

}(window.ImageDialog = window.ImageDialog || {}, jQuery ));
