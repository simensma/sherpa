$(document).ready(function() {

    var close_tag = 'div.dialog#dialog-image-fast-upload form.image-uploader div.tag-box div.tag a';
    $(document).on('mouseover', close_tag, function() {
        $(this).children("img").attr('src', '/static/img/so/close-hover.png');
    });
    $(document).on('mouseout', close_tag, function() {
        $(this).children("img").attr('src', '/static/img/so/close-default.png');
    });
    $(document).on('click', close_tag, function() {
        tagger.removeTag($(this).parent().text().trim());
        $(this).parent().remove();
    });

    var tagger = new Tagger($("div.dialog#dialog-image-fast-upload form.image-uploader input[name='tags']"), function(tag) {
        // New tag
        var tag = $('<div class="tag"><a href="javascript:undefined"><img src="/static/img/so/close-default.png"></a> ' + tag + '</div>');
        $("div.tag-box").append(tag);
    }, function(tag) {
        // Existing tag
        $("div.tag-box div.tag").each(function() {
            if($(this).text().trim().toLowerCase() == tag.toLowerCase()) {
                var item = $(this);
                var c = item.css('color');
                var bg = item.css('background-color');
                item.css('color', 'white');
                item.css('background-color', 'red');
                setTimeout(function() {
                    item.css('color', c);
                    item.css('background-color', bg);
                }, 1000);
            }
        });
    });

    $("div#dialog-image-fast-upload form").submit(function(e) {
        $("div#dialog-image-fast-upload div.uploading").show();
        var tags = JSON.stringify(tagger.tags);
        $("div.dialog#dialog-image-fast-upload form.image-uploader input[name='tags-serialized']").val(tags);
        $("div#dialog-image-fast-upload input[type='submit']").attr('disabled', 'disabled');
        $("div#dialog-image-fast-upload input[type='reset']").attr('disabled', 'disabled');
    });

    $("div#dialog-image-fast-upload button.cancel-upload").click(function(e) {
        uploadCancelled = false
        $("div#dialog-image-fast-upload").dialog("close");
    });
});

var uploadCompleteCallback;
var uploadCancelled = false;

function uploadComplete(status, url){
    if(!uploadCancelled){
        if(status === "no_files"){
            $("div#dialog-image-fast-upload input[type='submit']").removeAttr('disabled');
            $("div#dialog-image-fast-upload input[type='reset']").removeAttr('disabled');
            $("div#dialog-image-fast-upload div.upload-no-files").show();
            $("div#dialog-image-fast-upload div.uploading").hide();
        } else if(status === "success"){
            var description = $("div#dialog-image-fast-upload input[name='credits']").val();
            var photographer = $("div#dialog-image-fast-upload input[name='photographer']").val();
            $("div#dialog-image-fast-upload div.uploading").hide();
            $("div#dialog-image-fast-upload").dialog("close");
            uploadCompleteCallback(url, description, photographer);
        } else {//parse error or unexpected reply
            $("div#dialog-image-fast-upload input[type='submit']").removeAttr('disabled');
            $("div#dialog-image-fast-upload input[type='reset']").removeAttr('disabled');
            $("div#dialog-image-fast-upload div.upload-failed").show();
            $("div#dialog-image-fast-upload div.uploading").hide();
        }
    }
}

function openImageUpload(callback){
    uploadCancelled = false;
    uploadCompleteCallback = callback;

    $("div#dialog-image-fast-upload").dialog("open");
    $("div#dialog-image-fast-upload input[type='submit']").removeAttr('disabled');
    $("div#dialog-image-fast-upload input[type='reset']").removeAttr('disabled');
    resetImageUpload();
}

function resetImageUpload(){
    $("div#dialog-image-fast-upload input[type='reset']").click();
    $("div#dialog-image-fast-upload input[name='tags-serialized']").val("");
    $("div#dialog-image-fast-upload div.tag-box").empty();

    $("div#dialog-image-fast-upload div.uploading").hide();
    $("div#dialog-image-fast-upload div.upload-failed").hide();
    $("div#dialog-image-fast-upload div.upload-no-files").hide();
}
