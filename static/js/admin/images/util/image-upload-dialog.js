(function(ImageUploadDialog, $, undefined ) {

    /* Pick up DOM elements and bind events */

    var uploader;
    var form;
    var button_submit;
    var $tag_input;

    $(function() {
        uploader = $("div.image-upload-dialog");
        form = uploader.find("form");
        $tag_input = form.find('input[name="tags"]');
        button_submit = uploader.find('button[type="submit"]');

        Select2Tagger({$input: $tag_input});

        button_submit.click(function() {
            form.submit();
        });

        uploader.find("form").submit(function(e) {
            uploader.find("div.uploading").show();
            button_submit.prop('disabled', true);
        });

        var photographer = form.find("input[name='photographer']");
        SimpleTypeahead({
            url: photographer.attr('data-photographers-url'),
            $input: photographer,
        });
    });

    ImageUploadDialog.open = function(callback) {
        ImageUploadDialog.callback = callback;

        button_submit.prop('disabled', false);
        uploader.find("input[type='reset']").click();
        $tag_input.select2('val', '');

        // Hide that which should be hidden by default
        uploader.find("div.jq-hide").hide();

        uploader.modal();
    };

    window.iframeUploadComplete = iframeUploadComplete;
    function iframeUploadComplete(result) {
        if(result.status === "success") {
            var description = uploader.find("textarea[name='description']").val();
            var photographer = uploader.find("input[name='photographer']").val();
            uploader.find("div.uploading").hide();
            uploader.modal('hide');
            ImageUploadDialog.callback(result.url, description, photographer);
        } else if(result.status === "no_files") {
            button_submit.prop('disabled', false);
            uploader.find("div.upload-no-files").show();
            uploader.find("div.uploading").hide();
        } else if(result.status == 'parse_error') {
            button_submit.prop('disabled', false);
            uploader.find("div.parse-error").show();
            uploader.find("div.uploading").hide();
        } else if(result.status == 'unknown_exception') {
            button_submit.prop('disabled', false);
            uploader.find("div.unknown-exception").show();
            uploader.find("div.uploading").hide();
        }
    }

}(window.ImageUploadDialog = window.ImageUploadDialog || {}, jQuery ));
