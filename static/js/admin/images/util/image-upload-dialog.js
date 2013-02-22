$(document).ready(function() {

    var tagger = new TypicalTagger($("div.image-fast-upload form.image-uploader input[name='tags']"), $("div.image-fast-upload div.tag-box"));

    $("div.image-fast-upload form").submit(function(e) {
        $("div.image-fast-upload div.uploading").show();
        var tags = JSON.stringify(tagger.tags);
        $("div.image-fast-upload form.image-uploader input[name='tags-serialized']").val(tags);
        $("div.image-fast-upload input[type='submit']").attr('disabled', 'disabled');
        $("div.image-fast-upload input[type='reset']").attr('disabled', 'disabled');
    });

    $("div.image-fast-upload form input[name='photographer']").typeahead({
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

    $("div.image-fast-upload button.cancel-upload").click(function(e) {
        uploadCancelled = false;
        $("div.image-fast-upload").modal('hide');
    });
});

var uploadCompleteCallback;
var uploadCancelled = false;

function uploadComplete(status, url){
    if(!uploadCancelled){
        if(status === "no_files"){
            $("div.image-fast-upload input[type='submit']").removeAttr('disabled');
            $("div.image-fast-upload input[type='reset']").removeAttr('disabled');
            $("div.image-fast-upload div.upload-no-files").show();
            $("div.image-fast-upload div.uploading").hide();
        } else if(status === "success"){
            var description = $("div.image-fast-upload input[name='credits']").val();
            var photographer = $("div.image-fast-upload input[name='photographer']").val();
            $("div.image-fast-upload div.uploading").hide();
            $("div.image-fast-upload").modal('hide');
            uploadCompleteCallback(url, description, photographer);
        } else {//parse error or unexpected reply
            $("div.image-fast-upload input[type='submit']").removeAttr('disabled');
            $("div.image-fast-upload input[type='reset']").removeAttr('disabled');
            $("div.image-fast-upload div.upload-failed").show();
            $("div.image-fast-upload div.uploading").hide();
        }
    }
}

function openImageUpload(callback){
    uploadCancelled = false;
    uploadCompleteCallback = callback;

    $("div.image-fast-upload").modal();
    $("div.image-fast-upload input[type='submit']").removeAttr('disabled');
    $("div.image-fast-upload input[type='reset']").removeAttr('disabled');
    resetImageUpload();
}

function resetImageUpload(){
    $("div.image-fast-upload input[type='reset']").click();
    $("div.image-fast-upload input[name='tags-serialized']").val("");
    $("div.image-fast-upload div.tag-box").empty();

    $("div.image-fast-upload div.uploading").hide();
    $("div.image-fast-upload div.upload-failed").hide();
    $("div.image-fast-upload div.upload-no-files").hide();
}
