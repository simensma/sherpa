var userReady = false;
var uploadReady = false;

$(document).ready(function() {

    $("div.imagearchive-action-buttons button.upload").click(function() {
        $("div.uploader").toggle('slow');
    });

    var tagger = new TypicalTagger($("div.image-details input[name='tags']"), $("div.image-details div.tag-box"));

    /* Changing destination album */
    $("a.albumpicker-trigger").click(function() {
        AlbumPicker.open({
            album_id: $(this).attr('data-albumpicker-id'),
            allow_root: false,
            allow_deselect: true,
            picked: function(album) {
                if(album.name === '') {
                    album.name = "(Legges ikke i album)";
                }
                var form = $("form.upload-image-details");
                form.find("input[name='album']").val(album.id);
                form.find("p.chosen-album span.display-name").text(album.name);
                form.find("p.chosen-album a").attr('data-albumpicker-id', album.id);
            }
        });
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
                data: { name: query }
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

function iframeUploadComplete(result, ids) {
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
        $("div.upload-no-files").show();
        $("div.image-details").hide();
        $("form.image-uploader").show();
    } else if(result == 'unknown_exception') {
        $("div.upload-unknown-exception").show();
        $("div.image-details").hide();
        $("form.image-uploader").show();
    }
}
