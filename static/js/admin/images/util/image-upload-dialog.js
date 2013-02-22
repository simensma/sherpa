$(document).ready(function() {

    var tagger = new TypicalTagger($("div.image-upload-dialog form.image-uploader input[name='tags']"), $("div.image-upload-dialog div.tag-box"));

    $("div.image-upload-dialog form").submit(function(e) {
        $("div.image-upload-dialog div.uploading").show();
        var tags = JSON.stringify(tagger.tags);
        $("div.image-upload-dialog form.image-uploader input[name='tags-serialized']").val(tags);
        $("div.image-upload-dialog input[type='submit']").attr('disabled', 'disabled');
        $("div.image-upload-dialog input[type='reset']").attr('disabled', 'disabled');
    });

    $("div.image-upload-dialog form input[name='photographer']").typeahead({
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

    $("div.image-upload-dialog button.cancel-upload").click(function(e) {
        uploadCancelled = false;
        $("div.image-upload-dialog").modal('hide');
    });
});

var uploadCompleteCallback;
var uploadCancelled = false;

function uploadComplete(status, url){
    if(!uploadCancelled){
        if(status === "no_files"){
            $("div.image-upload-dialog input[type='submit']").removeAttr('disabled');
            $("div.image-upload-dialog input[type='reset']").removeAttr('disabled');
            $("div.image-upload-dialog div.upload-no-files").show();
            $("div.image-upload-dialog div.uploading").hide();
        } else if(status === "success"){
            var description = $("div.image-upload-dialog input[name='credits']").val();
            var photographer = $("div.image-upload-dialog input[name='photographer']").val();
            $("div.image-upload-dialog div.uploading").hide();
            $("div.image-upload-dialog").modal('hide');
            uploadCompleteCallback(url, description, photographer);
        } else {//parse error or unexpected reply
            $("div.image-upload-dialog input[type='submit']").removeAttr('disabled');
            $("div.image-upload-dialog input[type='reset']").removeAttr('disabled');
            $("div.image-upload-dialog div.upload-failed").show();
            $("div.image-upload-dialog div.uploading").hide();
        }
    }
}

function openImageUpload(callback){
    uploadCancelled = false;
    uploadCompleteCallback = callback;

    $("div.image-upload-dialog").modal();
    $("div.image-upload-dialog input[type='submit']").removeAttr('disabled');
    $("div.image-upload-dialog input[type='reset']").removeAttr('disabled');
    resetImageUpload();
}

function resetImageUpload(){
    $("div.image-upload-dialog input[type='reset']").click();
    $("div.image-upload-dialog input[name='tags-serialized']").val("");
    $("div.image-upload-dialog div.tag-box").empty();

    $("div.image-upload-dialog div.uploading").hide();
    $("div.image-upload-dialog div.upload-failed").hide();
    $("div.image-upload-dialog div.upload-no-files").hide();
}
