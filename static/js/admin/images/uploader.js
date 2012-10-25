var userReady = false;
var uploadReady = false;

$(document).ready(function() {

    $("div.imagearchive-action-buttons button.upload").click(function() {
        $("div.uploader").toggle('slow');
    });

    var close_tag = 'div.image-details div.tag-box div.tag a';
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

    var tagger = new Tagger($("div.image-details input[name='tags']"), function(tag) {
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

    /* Changing destination album */
    var picker = new AlbumPicker(false, function(album) {
        // Album picked
        $("form.upload-image-details input[name='album']").val(album.id);
        $("form.upload-image-details p.chosen-album span.display-name").text(album.name);
        $("form.upload-image-details p.chosen-album a").attr('data-albumpicker-id', album.id);
    });
    $("a.albumpicker-trigger").click(function() {
        picker.cd($(this).attr('data-albumpicker-id'));
    });

    $("form.image-uploader input[type='submit']").click(function() {
        $("form.image-uploader").hide();
        $("div.licencing").hide();
        $("div.uploading").show();
        $("div.image-details").show();
    });

    $("div.image-details form input[name='photographer']").typeahead({
        minLength: 3,
        source: function(query, process) {
            $.ajaxQueue({
                url: '/sherpa/bildearkiv/fotograf/',
                data: 'name=' + encodeURIComponent(query)
            }).done(function(result) {
                process(JSON.parse(result));
            });
        }
    });

    $("div.image-details form").submit(function(e) {
        if(uploadReady && userReady) {
            $("div.image-details input[name='tags-serialized']").val(JSON.stringify(tagger.tags));
        } else {
            e.preventDefault();
        }
    });

    $("div.image-details button[type='submit']").click(function(e) {
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
    } else if(result == 'unknown_exception') {
        $("div.upload-unknown-exception").show()
        $("div.image-details").hide();
        $("form.image-uploader").show();
    }
}
