$(document).ready(function() {
    var exif = false;
    $("#image-display div.exif").hide();
    $("#image-display a.toggle-exif").click(function() {
        if(exif) {
            $(this).text("Vis...");
            $("#image-display div.exif").hide();
            exif = false;
        } else {
            $(this).text("Skjul...");
            $("#image-display div.exif").show();
            exif = true;
        }
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
