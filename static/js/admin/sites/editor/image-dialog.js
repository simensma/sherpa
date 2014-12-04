(function(ImageDialog, $, undefined ) {

    var image_picked_callback; // Called when an image is picked in the dialog
    var image_removed_callback; // Called when an image is removed, from the dialog
    var image_dialog;
    var thumbnail_preview;
    var lookup_message;
    var not_found_message;
    var invalid_image_url_message;
    var input_photographer;
    var input_description;
    var input_url;
    var input_anchor;

    $(function() {

        image_dialog = $("div.cms-editor div.change-image");
        thumbnail_preview = image_dialog.find('.thumbnail img');
        lookup_message = image_dialog.find('.looking-up-image');
        not_found_message = image_dialog.find('.image-not-found');
        invalid_image_url_message = image_dialog.find('.invalid-image-url');
        input_photographer = image_dialog.find('input[name="photographer"]');
        input_description = image_dialog.find('input[name="description"]');
        input_url = image_dialog.find('input[name="src"]');
        input_anchor = image_dialog.find('input[name="anchor"]');

        image_dialog.find("button.choose-image").click(function() {
            ImageArchivePicker.pick(ImageDialog.insertImageDetails);
        });

        image_dialog.find("button.upload-image").click(function() {
            ImageUploadDialog.open(ImageDialog.insertImageDetails);
        });

        image_dialog.find("button.custom-url").click(function() {

            ImageDialog.resetDialog();
            ImageDialog.showUrlField();

            input_url.on('input', function (e) {

                var valid_image_url_regex = /\.(jpe?g|gif|png)$/i;
                var url = $(e.target).val();

                not_found_message.addClass('jq-hide');

                if (valid_image_url_regex.test(url)) {

                    invalid_image_url_message.addClass('jq-hide');
                    lookup_message.removeClass('jq-hide');
                    thumbnail_preview.attr('src', url);

                    thumbnail_preview.load(function () {
                        ImageDialog.showInfoFields();
                        lookup_message.addClass('jq-hide');
                    });

                    thumbnail_preview.error(function () {
                        ImageDialog.hideInfoFields();
                        if (!!$(this).attr('src')) {
                            lookup_message.addClass('jq-hide');
                            not_found_message.removeClass('jq-hide');
                        }
                    });

                } else {
                    ImageDialog.hideInfoFields();
                    invalid_image_url_message.removeClass('jq-hide');
                }

            });
        });

        image_dialog.find('button.insert-image').click(function() {
            var src = input_url.val().trim();
            if (src === '') {
                alert(image_dialog.attr('data-missing-url-warning'));
                return;
            }

            var anchor = input_anchor.val().trim();
            if (anchor.length !== 0 && !anchor.match(/^https?:\/\//)) {
                anchor = "http://" + anchor;
            }

            var description = input_description.val().trim();
            var photographer = input_photographer.val().trim();
            image_picked_callback(src, anchor, description, photographer);
            image_dialog.modal('hide');
        });

        SimpleTypeahead({
            url: input_photographer.attr('data-photographers-url'),
            $input: input_photographer,
        });
    });

    ImageDialog.resetDialog = function () {
        // Reset field values
        input_url.val('');
        input_anchor.val('');
        input_description.val('');
        input_photographer.typeahead('val', '');

        // Hide messages
        lookup_message.addClass('jq-hide');
        not_found_message.addClass('jq-hide');

        // Reset thumbnail
        thumbnail_preview.attr('src', '');

        // Hide fields
        image_dialog.find('.row.image-url').addClass('jq-hide');
        image_dialog.find('.row.image-info').addClass('jq-hide');
    };

    ImageDialog.hideInfoFields = function () {
        image_dialog.find('.row.image-info').addClass('jq-hide');
    };

    ImageDialog.showInfoFields = function () {
        image_dialog.find('.row.image-info').removeClass('jq-hide');
    };

    ImageDialog.showUrlField = function () {
        image_dialog.find('.row.image-url').removeClass('jq-hide');
    };

    ImageDialog.insertImageDetails = function (url, description, photographer) {
        ImageDialog.resetDialog();
        ImageDialog.showInfoFields();

        thumbnail_preview.attr('src', url);
        input_url.val(url);
        input_description.val(description);
        input_photographer.typeahead('val', photographer);
    };

    ImageDialog.open = function(opts) {

        this.resetDialog();

        image_picked_callback = opts.save;
        image_removed_callback = opts.remove;

        var is_new = !!opts.src.match(/placeholder\.png/);
        var is_external = !opts.src.match(/cdn\.turistforeningen|cdn\.dnt/);

        if (!is_new) {

            if (is_external) {
                this.showUrlField();
            }

            // Important to insert image details first, as this resets all fields
            this.insertImageDetails(opts.src, opts.description, opts.photographer);

            input_anchor.val(opts.anchor);
        }

        image_dialog.modal();
    };

}(window.ImageDialog = window.ImageDialog || {}, jQuery ));
