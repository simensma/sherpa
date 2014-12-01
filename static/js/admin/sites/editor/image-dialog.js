(function(ImageDialog, $, undefined ) {

    var image_picked_callback; // Called when an image is picked in the dialog
    var image_removed_callback; // Called when an image is removed, from the dialog
    var image_dialog;

    $(function() {

        image_dialog = $("div.cms-editor div.change-image");

        image_dialog.find("button.choose-image").click(function() {
            ImageArchivePicker.pick(ImageDialog.insertImageDetails);
        });

        image_dialog.find("button.upload-image").click(function() {
            ImageUploadDialog.open(ImageDialog.insertImageDetails);
        });

        image_dialog.find("button.custom-url").click(function() {

            // $(this).addClass('active');

            ImageDialog.resetDialog();
            ImageDialog.showUrlField();

            image_dialog.find('input[name="src"]').on('input', function (e) {
                var valid_image_url_regex = /\.(jpe?g|gif|png)$/i;
                var url = $(e.target).val();

                if (valid_image_url_regex.test(url)) {
                    image_dialog.find('.thumbnail img').attr('src', url);
                    // jQuery( document ).on( 'error', 'img', function( e ){
                    //     $( this ).addClass( 'missing-image' ).attr( 'src', 'url/to/missing.png' );
                    // });
                    // <img onerror="this.style.display='none'" src="">
                    ImageDialog.showInfoFields();
                }

            });
        });

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
        SimpleTypeahead({
            url: photographer.attr('data-photographers-url'),
            $input: photographer,
        });
    });

    ImageDialog.resetDialog = function () {
        // image_dialog.find('.image-choices button').removeClass('active');
        image_dialog.find('.image-url').addClass('jq-hide');
        image_dialog.find('.image-info').addClass('jq-hide');
        image_dialog.find('input[name="src"]').val('');
        image_dialog.find('input[name="anchor"]').val('');
        image_dialog.find('input[name="description"]').val('');
        image_dialog.find('input[name="photographer"]').val('');
    };

    ImageDialog.showInfoFields = function () {
        image_dialog.find('.image-info').removeClass('jq-hide');
    };

    ImageDialog.showUrlField = function () {
        image_dialog.find('.row.image-url').removeClass('jq-hide');
    };

    ImageDialog.insertImageDetails = function (url, description, photographer) {
        ImageDialog.resetDialog();
        ImageDialog.showInfoFields();

        image_dialog.find('.thumbnail img').attr('src', url);
        image_dialog.find("input[name='src']").val(url);
        image_dialog.find("input[name='description']").val(description);
        image_dialog.find("input[name='photographer']").val(photographer);
    };

    ImageDialog.open = function(opts) {

        this.resetDialog();

        image_picked_callback = opts.save;
        image_removed_callback = opts.remove;

        var is_new = !!opts.src.match(/placeholder\.png/);
        var is_external = !opts.src.match(/cdn\.turistforeningen|cdn\.dnt/);

        if (is_new) {

        } else {

            if (is_external) {
                // image_dialog.find('.image-choices .btn.custom-url').addClass('active');
                this.showUrlField();
            } else {
                // image_dialog.find('.image-choices .btn.choose-image').addClass('active');
            }

            image_dialog.find("input[name='anchor']").val(opts.anchor);

            this.insertImageDetails(opts.src, opts.description, opts.photographer);
        }

        image_dialog.modal();
    };

}(window.ImageDialog = window.ImageDialog || {}, jQuery ));
