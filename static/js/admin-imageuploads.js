$(document).ready(function() {

    $("div.uploading").hide();
    $("div.image-details").hide();
    $("div.image-details p.waiting").hide();
    $("div.messages").children().each(function() {
        $(this).hide();
    });

    $("div.image-details form").submit(function(e) {
        if(!uploadReady) {
            e.preventDefault();
            userReady = true;
            $("div.image-details input[type='submit']").attr('disabled', true);
            $("div.image-details p.waiting").show();
        }
    });

    $("input[type='submit']").click(function() {
        $("form.image-uploader").hide();
        $("div.uploading").show();
        $("div.image-details").show();
    });

});

var userReady = false;
var uploadReady = false;

function uploadComplete(result, ids) {
    $("div.uploading").hide();
    if(result == 'success') {
        $("div.upload-complete").show();
        $("div.image-details input[name='ids']").val(ids);
        uploadReady = true;
        if(userReady) {
            $("div.image-details form").trigger('submit');
        }
    } else if(result == 'parse_error') {
        $("div.upload-failed").show();
        $("div.image-details").hide();
        $("form.image-uploader").show();
    } else if(result == 'no_files') {
        $("div.upload-no-files").show()
        $("div.image-details").hide();
        $("form.image-uploader").show();
    }
}
