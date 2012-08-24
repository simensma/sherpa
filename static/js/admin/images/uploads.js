var userReady = false;
var uploadReady = false;

$(document).ready(function() {

    var tagger = new Tagger($("div.image-details input[name='tags']"), function(tag) {
        // New tag
        var tag = $('<div class="tag">' + tag + ' <a href="javascript:undefined"><img src="/static/img/so/close-default.png"></a></div>');
        var a = tag.find('a');
        a.hover(function() { $(this).children("img").attr('src', '/static/img/so/close-hover.png'); },
                function() { $(this).children("img").attr('src', '/static/img/so/close-default.png'); });
        a.click(function() {
            tagger.removeTag($(this).parent().text().trim());
            $(this).parent().remove();
        });
        $("div#tags").append(tag);
    }, function(tag) {
        // Existing tag
        $("div#tags div.tag").each(function() {
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

    $("div.uploading").hide();
    $("div.image-details").hide();
    $("div.image-details p.waiting").hide();
    $("div.messages").children().each(function() {
        $(this).hide();
    });

    $("form.image-uploader input[type='submit']").click(function() {
        $("form.image-uploader").hide();
        $("div.uploading").show();
        $("div.image-details").show();
    });

    $("div.image-details form").submit(function(e) {
        if(uploadReady && userReady) {
            $("div.image-details input[name='tags-serialized']").val(JSON.stringify(tagger.tags));
        } else {
            e.preventDefault();
        }
    });

    $("div.image-details input[type='submit']").click(function(e) {
        userReady = true;
        if(!uploadReady) {
            e.preventDefault();
            $("div.image-details input[type='submit']").attr('disabled', true);
            $("div.image-details p.waiting").show();
        }
    });

});

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

