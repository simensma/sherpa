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
    $(document).on('click', "a[data-albumpicker-id]", function() {
        var ajaxloader = $("div.album-picker img.ajaxloader");
        var path = $("div.album-picker div.albumpath span.path");
        var children = $("div.album-picker div.children");
        path.empty();
        children.empty();
        ajaxloader.show();
        var album_id = $(this).attr('data-albumpicker-id');
        var url = album_id;
        if(url != '') {
            url += '/';
        }

        $.ajax({
            url: '/sherpa/bildearkiv/innhold/album/' + url,
        }).done(function(result) {
            result = JSON.parse(result);

            // Set current to that one
            $("div.album-picker div.albumpath").attr('data-current-album', album_id);
            if(result.path.length > 0) {
                $("div.album-picker div.albumpath").attr('data-current-album-name', result.path[result.path.length-1].name);
            } else {
                $("div.album-picker div.albumpath").attr('data-current-album-name', "Bildearkiv");
            }

            // Re-enter path
            for(var i=0; i<result.path.length; i++) {
                path.append(' / <a href="javascript:undefined" data-albumpicker-id="' + result.path[i].id + '">' + result.path[i].name + '</a>');
            }

            // Apply album children
            for(var i=0; i<result.albums.length; i++) {
                var clone = $("div.dummy-child").clone();
                clone.removeClass('dummy-child').addClass('child');
                clone.find("a").text(result.albums[i].name).attr('data-albumpicker-id', result.albums[i].id);
                children.append(clone);
                clone.show();
            }
            if(result.albums.length == 0) {
                children.append('<p>Ingen underalbum i dette albumet. Klikk "Velg dette albumet" over hvis du vil velge dette albumet.</p>');
            }
        }).fail(function(result) {
            // Todo
        }).always(function(result) {
            ajaxloader.hide();
        });
    });

    $("div.album-picker button.pick").click(function() {
        var album_name = $("div.album-picker div.albumpath").attr('data-current-album-name');
        var album_id = $("div.album-picker div.albumpath").attr('data-current-album');
        $("form.upload-image-details input[name='album']").val(album_id);
        $("form.upload-image-details a[data-albumpicker-id]").attr('data-albumpicker-id', album_id).text(album_name);
        $("div.album-picker").dialog('close');
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
