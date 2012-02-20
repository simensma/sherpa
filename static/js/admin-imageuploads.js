var tags; // will be overridden by template

$(document).ready(function() {

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
            serializeTags();
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

    // Enable autocomplete, parse tags on focus out, and when user presses space
    // and the last character is a space
    $("div.image-details input[name='tags']").autocomplete({
        source: tags,
        open: function() { autocomplete = true; },
        close: function() { $(this).val(""); autocomplete = false; },
        select: function(event, ui) {
            addTags(ui.item.value);
        }
    }).keydown(function(e) {
        if(e.which == 13) {
            // Add the tag if user presses enter.
            e.preventDefault();
            addTags($(this).val());
            $(this).val("");
        }
    }).keyup(function(e) {
        var val = $(this).val();
        if(val.length > 1 && val[val.length-1] == ' ') {
            addTags(val);
            $(this).val("");
        }
    }).focusout(function() {
        if(!autocomplete) {
            addTags($(this).val());
            $(this).val("");
        }
    });
});

var autocomplete = false;
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

/* Attaches the given tag names to the DOM */
function addTags(tags) {
    tags = tags.split(' ');
    for(var i=0; i<tags.length; i++) {
        // Drop empty tags
        if(tags[i] == "") { continue; }

        // Don't add already added tags
        var cont = true;
        $("div#tags div.tag").each(function() {
            if($(this).text() == tags[i]) {
                var item = $(this);
                var c = item.css('color');
                var bg = item.css('background-color');
                item.css('color', 'white');
                item.css('background-color', 'red');
                setTimeout(function() {
                    item.css('color', c);
                    item.css('background-color', bg);
                }, 1000);
                cont = false;
            }
        });
        if(!cont) { continue; }

        // Now create the tag
        var el = $(document.createElement("div"));
        var a = $(document.createElement("a"));
        var img = $(document.createElement("img"));
        img.attr('src', '/static/img/so/close-default.png');
        a.hover(function() { $(this).children("img").attr('src', '/static/img/so/close-hover.png'); },
                function() { $(this).children("img").attr('src', '/static/img/so/close-default.png'); });
        a.click(function() { $(this).parent().remove(); });
        a.append(img);
        el.addClass('tag').text(tags[i]).append(a);
        $("div#image-uploader div#tags").append(el);
    }
}

function serializeTags() {
    var list = "["
    $("div#tags").children().each(function() {
        if(list.length > 1) {
            list += ", "
        }
        list += "\"" + $(this).text().replace(/"/g, "\\\"").replace(/\\/g, "\\\\") + "\"";
    });
    list += "]"
    $("div.image-details input[name='tags-serialized']").val(list);
}
