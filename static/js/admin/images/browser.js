$(document).ready(function() {

    // New image-button
    $("div.imagearchive-action-buttons button.upload").click(function() {
        window.location = $(this).attr('data-href');
    });

    var dialog;
    $("button.details").click(function() {
        dialog.dialog('open');
    });

    $(".album-details form").submit(function() {
        var albums = [];
        $("#archive-gallery li.album.selected").each(function() {
            albums.push($(this).attr('data-id'));
        });
        $(this).children("input[name='albums']").val(JSON.stringify(albums));
    });

    $("button.context").attr('disabled', true);
    function toggleMultiedit() {
        var albums = $("#archive-gallery li.album.selected").length > 0;
        var images = $("#archive-gallery li.image.selected").length > 0;
        if(albums && images) {
            $("div.imagearchive-action-buttons button.delete").removeAttr('disabled');
            $("div.imagearchive-action-buttons button.details").attr('disabled', true);
            $("div.delete-dialog p").text('Er du helt sikker på at du vil slette alle albumene og bildene du har merket, for godt? Alle underalbum og bilder i merkede album vil også bli slettet for godt.');
            $("div.imagearchive-action-buttons button.delete").html('<i class="icon-remove"></i> Slett album og bilder');
        } else if(albums) {
            $("div.imagearchive-action-buttons button.context").removeAttr('disabled');
            $("div.delete-dialog p").text('Er du helt sikker på at du vil slette alle albumene du har merket, for godt? Alle underalbum og bilder i albumet vil også bli slettet for godt.');
            $("div.imagearchive-action-buttons button.details").html('<i class="icon-pencil"></i> Endre albumdetaljer');
            $("div.imagearchive-action-buttons button.delete").html('<i class="icon-remove"></i> Slett album');
            dialog = $(".album-details.dialog");
        } else if(images) {
            $("div.imagearchive-action-buttons button.context").removeAttr('disabled');
            $("div.delete-dialog p").text('Er du helt sikker på at du vil slette alle bildene du har merket, for godt?');
            $("div.imagearchive-action-buttons button.details").html('<i class="icon-pencil"></i> Endre bildedetaljer');
            $("div.imagearchive-action-buttons button.delete").html('<i class="icon-remove"></i> Slett bilder');
        } else {
            $("div.imagearchive-action-buttons button.context").attr('disabled', true);
        }
    }

    $("#archive-gallery li.album button.mark").click(function() {
        $(this).parent("li").toggleClass('selected');
        toggleMultiedit();
    });

    $("#archive-gallery li.image button.mark").click(function() {
        $(this).parent("li").toggleClass('selected');
        toggleMultiedit();
    });

    $(".delete-dialog button").click(function() {
        $(".delete-dialog").dialog('close');
    });
    $(".delete-dialog form").submit(function() {
        var albums = [];
        var images = [];
        $("#archive-gallery li.album.selected").each(function() {
            albums.push($(this).attr('data-id'));
        });
        $("#archive-gallery li.image.selected").each(function() {
            images.push($(this).attr('data-id'));
        });
        $(this).find("input[name='albums']").val(JSON.stringify(albums));
        $(this).find("input[name='images']").val(JSON.stringify(images));
    });

});
