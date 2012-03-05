$(document).ready(function() {

    var selected;
    $("div.multiedit").hide();
    function toggleMultiedit() {
        if($("#archive-gallery li.selected").length > 0) {
            $("div.multiedit").show();
        } else {
            $("div.multiedit").hide();
        }
    }

    $("#archive-gallery li.album button.mark").click(function() {
        $("#archive-gallery li.image.selected").removeClass('selected');
        $(this).parent("li").toggleClass('selected');
        selected = 'album';
        toggleMultiedit();
    });

    $("#archive-gallery li.image button.mark").click(function() {
        $("#archive-gallery li.album.selected").removeClass('selected');
        $(this).parent("li").toggleClass('selected');
        selected = 'image';
        toggleMultiedit();
    });

    $(".delete-dialog button").click(function() {
        $(".delete-dialog").dialog('close');
    });
    $(".delete-dialog button.perform-delete").click(function() {
        var albums = [];
        var images = [];
        $("#archive-gallery li.album.selected").each(function() {
            albums = albums.concat([$(this).attr('data-id')]);
        });
        $("#archive-gallery li.image.selected").each(function() {
            images = images.concat([$(this).attr('data-id')]);
        });
        $(this).siblings("input[name='albums']").val(JSON.stringify(albums));
        $(this).siblings("input[name='images']").val(JSON.stringify(images));
    });

    $("div.multiedit button").click(function() {
        if(selected == 'album') {
            $("div.delete-dialog p").text('Er du helt sikker på at du vil slette alle albumene du har merket, for godt? Alle underalbum og bilder i albumet vil også bli slettet for godt.');
        } else if(selected == 'image') {
            $("div.delete-dialog p").text('Er du helt sikker på at du vil slette alle bildene du har merket, for godt?');
        }
    });

});
