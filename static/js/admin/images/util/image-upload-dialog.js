$(document).ready(function() {

    var uploader = $("div.image-upload-dialog");
    var tagger = new TypicalTagger(uploader.find("form.image-uploader input[name='tags']"), uploader.find("div.tag-box"));

    uploader.find("form").submit(function(e) {
        uploader.find("div.uploading").show();
        var tags = JSON.stringify(tagger.tags);
        uploader.find("form.image-uploader input[name='tags-serialized']").val(tags);
        uploader.find("input[type='submit']").attr('disabled', 'disabled');
        uploader.find("input[type='reset']").attr('disabled', 'disabled');
    });

    uploader.find("form input[name='photographer']").typeahead({
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

    var uploadCompleteCallback;

    window.uploadComplete = uploadComplete;
    function uploadComplete(status, url){
        if(status === "no_files"){
            uploader.find("input[type='submit']").removeAttr('disabled');
            uploader.find("input[type='reset']").removeAttr('disabled');
            uploader.find("div.upload-no-files").show();
            uploader.find("div.uploading").hide();
        } else if(status === "success"){
            var description = uploader.find("input[name='credits']").val();
            var photographer = uploader.find("input[name='photographer']").val();
            uploader.find("div.uploading").hide();
            $("div.image-upload-dialog").modal('hide');
            uploadCompleteCallback(url, description, photographer);
        } else {//parse error or unexpected reply
            uploader.find("input[type='submit']").removeAttr('disabled');
            uploader.find("input[type='reset']").removeAttr('disabled');
            uploader.find("div.upload-failed").show();
            uploader.find("div.uploading").hide();
        }
    }

    window.openImageUpload = openImageUpload;
    function openImageUpload(callback){
        uploadCompleteCallback = callback;

        $("div.image-upload-dialog").modal();
        uploader.find("input[type='submit']").removeAttr('disabled');
        uploader.find("input[type='reset']").removeAttr('disabled');
        resetImageUpload();
    }

    function resetImageUpload(){
        uploader.find("input[type='reset']").click();
        uploader.find("input[name='tags-serialized']").val("");
        uploader.find("div.tag-box").empty();

        uploader.find("div.uploading").hide();
        uploader.find("div.upload-failed").hide();
        uploader.find("div.upload-no-files").hide();
    }
});
