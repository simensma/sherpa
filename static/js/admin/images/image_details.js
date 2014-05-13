$(function() {
    var image_details = $("div.image-details");
    var exif = image_details.find("div.exif");
    image_details.find("a.toggle-exif").click(function() {
        var alt = $(this).attr('data-alt');
        $(this).attr('data-alt', $(this).text());
        $(this).text(alt);
        exif.toggle();
    });

    $("form.delete-image").submit(function(e) {
        if(!confirm("Er du sikker på at du vil slette dette bildet for godt?\n\nDu kan ikke angre denne avgjørelsen.")) {
            e.preventDefault();
        }
    });

    $("button.move-image").click(function() {
        var album_id = $(this).attr('data-album-id');
        AlbumPicker.open({
            album_id: album_id,
            allow_root: false,
            allow_deselect: true,
            picked: function(album) {
                var form = $("form.move-image");
                form.find("input[name='destination_album']").val(album.id);
                form.submit();
            }
        });
    });
});
