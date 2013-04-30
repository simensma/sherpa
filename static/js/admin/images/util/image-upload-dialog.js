(function(ImageUploadDialog, $, undefined ) {

    /* Pick up DOM elements and bind events */

    var uploader;
    var form;
    var tagger;
    $(document).ready(function() {
        uploader = $("div.image-upload-dialog");
        form = uploader.find("form");
        tagger = new TypicalTagger(form.find("input[name='tags']"), uploader.find("div.tag-box"));

        uploader.find("form").submit(function(e) {
            uploader.find("div.uploading").show();
            var tags = JSON.stringify(tagger.tags);
            form.find("input[name='tags-serialized']").val(tags);
            uploader.find("input[type='submit']").attr('disabled', 'disabled');
        });

        form.find("input[name='photographer']").typeahead({
            minLength: 3,
            source: function(query, process) {
                $.ajaxQueue({
                    url: '/sherpa/bildearkiv/fotograf/',
                    data: { name: query }
                }).done(function(result) {
                    process(JSON.parse(result));
                });
            }
        });
    });

    ImageUploadDialog.open = function(callback) {
        ImageUploadDialog.callback = callback;

        uploader.find("input[type='submit']").removeAttr('disabled');
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
            uploader.find("input[type='submit']").removeAttr('disabled');
            uploader.find("div.upload-no-files").show();
            uploader.find("div.uploading").hide();
        } else if(result.status == 'parse_error') {
            uploader.find("input[type='submit']").removeAttr('disabled');
            uploader.find("div.parse-error").show();
            uploader.find("div.uploading").hide();
        } else if(result.status == 'unknown_exception') {
            uploader.find("input[type='submit']").removeAttr('disabled');
            uploader.find("div.unknown-exception").show();
            uploader.find("div.uploading").hide();
        }
    }

}(window.ImageUploadDialog = window.ImageUploadDialog || {}, jQuery ));
