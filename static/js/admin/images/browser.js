$(document).ready(function() {

    var dialog;
    $("button.details-button").click(function() {
        dialog.dialog('open');
    });

    $(".album-details form").submit(function() {
        var albums = [];
        $("#archive-gallery li.album.selected").each(function() {
            albums.push($(this).attr('data-id'));
        });
        $(this).children("input[name='albums']").val(JSON.stringify(albums));
    });

    $(".image-details form").submit(function() {
        var images = [];
        $("#archive-gallery li.image.selected").each(function() {
            images.push($(this).attr('data-id'));
        });
        $(this).children("input[name='ids']").val(JSON.stringify(images));
        $(this).find("input[name='tags-serialized']").val(JSON.stringify(tagger.tags));
    });

    $("button.context-button").attr('disabled', true);
    function toggleMultiedit() {
        var albums = $("#archive-gallery li.album.selected").length > 0;
        var images = $("#archive-gallery li.image.selected").length > 0;
        if(albums && images) {
            $("table.action-buttons button.delete-button").removeAttr('disabled');
            $("table.action-buttons button.details-button").attr('disabled', true);
            $("div.delete-dialog p").text('Er du helt sikker på at du vil slette alle albumene og bildene du har merket, for godt? Alle underalbum og bilder i merkede album vil også bli slettet for godt.');
            $("table.action-buttons button.delete-button").html('<i class="icon-remove"></i> Slett album og bilder');
        } else if(albums) {
            $("table.action-buttons button.context-button").removeAttr('disabled');
            $("div.delete-dialog p").text('Er du helt sikker på at du vil slette alle albumene du har merket, for godt? Alle underalbum og bilder i albumet vil også bli slettet for godt.');
            $("table.action-buttons button.details-button").html('<i class="icon-pencil"></i> Endre albumdetaljer');
            $("table.action-buttons button.delete-button").html('<i class="icon-remove"></i> Slett album');
            dialog = $(".album-details.dialog");
        } else if(images) {
            $("table.action-buttons button.context-button").removeAttr('disabled');
            $("div.delete-dialog p").text('Er du helt sikker på at du vil slette alle bildene du har merket, for godt?');
            $("table.action-buttons button.details-button").html('<i class="icon-pencil"></i> Endre bildedetaljer');
            $("table.action-buttons button.delete-button").html('<i class="icon-remove"></i> Slett bilder');
            dialog = $(".image-details.dialog");
        } else {
            $("table.action-buttons button.context-button").attr('disabled', true);
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

    // Enable tagging
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

});
