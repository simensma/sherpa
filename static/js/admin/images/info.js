$(document).ready(function() {

    var autocompleteobject = {
        source: "/sherpa/bildearkiv/tag/filter/",
        open: function() { autocomplete = true; },
        close: function() { autocomplete = false; },
        select: function(event, ui) {
            event.preventDefault();
            $(this).val("");
            addTags(ui.item.value);
        }
    };

    function keydown(e) {
        if(e.which == 13) {
            // Add the tag if user presses enter.
            e.preventDefault();
            addTags($(this).val());
            $(this).val("");
        }
    }
    function keyup(e) {
        var val = $(this).val();
        if(val.length > 1 && val[val.length-1] == ' ') {
            addTags(val);
            $(this).val("");
        }
    }
    function focusout() {
        if(!autocomplete) {
            addTags($(this).val());
            $(this).val("");
        }
    }

    // Enable autocomplete, parse tags on focus out, and when user presses space
    // and the last character is a space
    $("div.image-details input[name='tags']").autocomplete(autocompleteobject).keydown(keydown).keyup(keyup).focusout(focusout);
    $("div.dialog#dialog-image-fast-upload form.image-uploader input[name='tags']").autocomplete(autocompleteobject).keydown(keydown).keyup(keyup).focusout(focusout);
});

var autocomplete = false;
var userReady = false;
var uploadReady = false;

/* Attaches the given tag names to the DOM */
function addTags(tags) {
    tags = tags.split(' ');
    for(var i=0; i<tags.length; i++) {
        // Drop empty tags
        if(tags[i] == "") { continue; }

        //comma is commonly associated with seperation of tags and other stuff, they are very likely not supposed to be there
        tags[i] = tags[i].replace(",", "");

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
        $("div#tags").append(el);
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
    $("div.dialog#dialog-image-fast-upload form.image-uploader input[name='tags-serialized']").val(list);
}
