(function(ImageUploadDialog, $, undefined ) {

    /* Pick up DOM elements and bind events */

    var uploader;
    var form;
    $(document).ready(function() {
        uploader = $("div.image-upload-dialog");
        form = uploader.find("form");

        TagDisplay.enable({
            ref: 'image-upload-dialog',
            targetInput: form.find("input[name='tags-serialized']"),
            tagBox: uploader.find("div.tag-box"),
            pickerInput: form.find("input[name='tags']")
        });

        uploader.find("form").submit(function(e) {
            uploader.find("div.uploading").show();
            uploader.find("input[type='submit']").prop('disabled', true);
            TagDisplay.collect('image-upload-dialog');
        });

        var photographer = form.find("input[name='photographer']");
        photographer.typeahead({
            minLength: 3,
            source: function(query, process) {
                $.ajaxQueue({
                    url: photographer.attr('data-source-url'),
                    data: { name: query }
                }).done(function(result) {
                    process(JSON.parse(result));
                });
            }
        });
    });

    ImageUploadDialog.open = function(callback) {
        ImageUploadDialog.callback = callback;

        uploader.find("input[type='submit']").prop('disabled', false);
        uploader.find("input[type='reset']").click();

        uploader.find("input[name='tags-serialized']").val("");
        uploader.find("div.tag-box").empty();

        // Hide that which should be hidden by default
        uploader.find("div.hide").hide();

        uploader.modal();
    };

    window.iframeUploadComplete = iframeUploadComplete;
    function iframeUploadComplete(result) {
        if(result.status === "success") {
            var description = uploader.find("input[name='credits']").val();
            var photographer = uploader.find("input[name='photographer']").val();
            uploader.find("div.uploading").hide();
            uploader.modal('hide');
            ImageUploadDialog.callback(result.url, description, photographer);
        } else if(result.status === "no_files") {
            uploader.find("input[type='submit']").prop('disabled', false);
            uploader.find("div.upload-no-files").show();
            uploader.find("div.uploading").hide();
        } else if(result.status == 'parse_error') {
            uploader.find("input[type='submit']").prop('disabled', false);
            uploader.find("div.parse-error").show();
            uploader.find("div.uploading").hide();
        } else if(result.status == 'unknown_exception') {
            uploader.find("input[type='submit']").prop('disabled', false);
            uploader.find("div.unknown-exception").show();
            uploader.find("div.uploading").hide();
        }
    }

}(window.ImageUploadDialog = window.ImageUploadDialog || {}, jQuery ));
