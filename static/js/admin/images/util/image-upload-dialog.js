(function(ImageUploadDialog, $, undefined ) {

    /* Pick up DOM elements and bind events */

    var uploader;
    var form;
    var button_submit;

    $(function() {
        uploader = $("div.image-upload-dialog");
        form = uploader.find("form");
        button_submit = uploader.find('button[type="submit"]');

        TagDisplay.enable({
            ref: 'image-upload-dialog',
            targetInput: form.find("input[name='tags-serialized']"),
            tagBox: uploader.find("div.tag-box"),
            pickerInput: form.find("input[name='tags']")
        });

        button_submit.click(function() {
            form.submit();
        });

        uploader.find("form").submit(function(e) {
            uploader.find("div.uploading").show();
            button_submit.prop('disabled', true);
            TagDisplay.collect('image-upload-dialog');
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

        uploader.find("input[name='tags-serialized']").val("");
        uploader.find("div.tag-box").empty();

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
