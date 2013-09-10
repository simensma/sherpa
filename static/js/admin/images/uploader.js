var userReady = false;
var uploadReady = false;

$(document).ready(function() {

    $("div.imagearchive-action-buttons button.upload").click(function() {
        $("div.uploader").toggle('slow');
    });

    TagDisplay.enable({
        targetInput: $("div.image-details input[name='tags-serialized']"),
        tagBox: $("div.image-details div.tag-box"),
        pickerInput: $("div.image-details input[name='tags']")
    });

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

    var photographer = $("div.image-details form input[name='photographer']");
    photographer.typeahead({
        minLength: 3,
        source: function(query, process) {
            $.ajaxQueue({
                url: photographer.attr('data-source-url'),
                data: { name: query }
            }).done(function(result) {
                process(JSON.parse(result));
            });
        }
    });

    $("div.image-details form").submit(function(e) {
        if(uploadReady && userReady) {
            TagDisplay.collect();
        } else {
            e.preventDefault();
        }
    });

    $("div.image-details button[type='submit']").click(function(e) {
        userReady = true;
        if(!uploadReady) {
            e.preventDefault();
            $(this).prop('disabled', true);
            $("div.image-details p.waiting").show();
        }
    });
});

function iframeUploadComplete(result) {
    $("div.uploading").hide();
    if(result.status == 'success') {
        $("div.upload-complete").show();
        $("div.image-details input[name='ids']").val(JSON.stringify(result.ids));
        uploadReady = true;
        if(userReady) {
            $("div.image-details form").trigger('submit');
        }
    } else if(result.status == 'no_files') {
        $("div.upload-no-files").show();
        $("div.image-details").hide();
        $("form.image-uploader").show();
    } else if(result.status == 'parse_error') {
        $("div.upload-failed").show();
        $("div.image-details").hide();
        $("form.image-uploader").show();
    } else if(result.status == 'unknown_exception') {
        $("div.upload-unknown-exception").show();
        $("div.image-details").hide();
        $("form.image-uploader").show();
    }
}
