var userReady = false;
var uploadReady = false;

var iframeCallbackSuccess = false;
var iframeUploadComplete;

$(document).ready(function() {

    var uploader = $("div.uploader");
    var uploading = uploader.find("div.uploading");
    var licencing = uploader.find("div.licencing");
    var image_details = uploader.find("div.image-details");
    var form_image = uploader.find("form.image-uploader");
    var form_details = image_details.find("form.upload-image-details");
    var iframe = uploader.find("iframe");

    $("div.imagearchive-action-buttons button.upload").click(function() {
        uploader.toggle('slow');
    });

    TagDisplay.enable({
        targetInput: image_details.find("input[name='tags-serialized']"),
        tagBox: image_details.find("div.tag-box"),
        pickerInput: image_details.find("input[name='tags']")
    });

    /* Changing destination album */
    uploader.find("a.albumpicker-trigger").click(function() {
        AlbumPicker.open({
            album_id: $(this).attr('data-albumpicker-id'),
            allow_root: false,
            allow_deselect: true,
            picked: function(album) {
                if(album.name === '') {
                    album.name = "(Legges ikke i album)";
                }
                form_details.find("input[name='album']").val(album.id);
                form_details.find("p.chosen-album span.display-name").text(album.name);
                form_details.find("p.chosen-album a").attr('data-albumpicker-id', album.id);
            }
        });
    });

    form_image.find("input[type='submit']").click(function() {
        form_image.hide();
        licencing.hide();
        uploading.show();
        image_details.show();
    });

    iframe.load(function() {
        setTimeout(function() {
            if(!iframeCallbackSuccess) {
                // Well, the iframe loaded but callback-success wasn't set. Maybe a timeout or something happened,
                // we didn't render the expected result at least. Show an error.
                uploading.hide();
                uploader.find("div.upload-iframe-render-failed").show();
            }
        }, 1000);
    });

    var photographer = form_details.find("input[name='photographer']");
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

    form_details.submit(function(e) {
        if(uploadReady && userReady) {
            TagDisplay.collect();
        } else {
            e.preventDefault();
        }
    });

    image_details.find("button[type='submit']").click(function(e) {
        userReady = true;
        if(!uploadReady) {
            e.preventDefault();
            $(this).prop('disabled', true);
            image_details.find("p.waiting").show();
        }
    });

    iframeUploadComplete = function(result) {
        iframeCallbackSuccess = true;
        uploading.hide();
        if(result.status == 'success') {
            uploader.find("div.upload-complete").show();
            image_details.find("input[name='ids']").val(JSON.stringify(result.ids));
            uploadReady = true;
            if(userReady) {
                form_details.trigger('submit');
            }
        } else if(result.status == 'no_files') {
            uploader.find("div.upload-no-files").show();
            image_details.hide();
            form_image.show();
        } else if(result.status == 'parse_error') {
            uploader.find("div.upload-failed").show();
            image_details.hide();
            form_image.show();
        } else if(result.status == 'unknown_exception') {
            uploader.find("div.upload-unknown-exception").show();
            image_details.hide();
            form_image.show();
        }
    };
});
