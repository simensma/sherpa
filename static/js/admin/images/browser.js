$(document).ready(function() {

    var actionButtons = $("div.imagearchive-action-buttons");

    actionButtons.find("button.albums.details").click(function() {
        $(".album-details.dialog").dialog('open');
    });
    actionButtons.find("button.images.details").click(function() {
        var images = [];
        $("#archive-gallery li.image.selected").each(function() {
            images.push($(this).attr('data-id'));
        });
        window.location = '/sherpa/bildearkiv/bilde/oppdater/?bilder=' + encodeURIComponent(JSON.stringify(images)) + '&origin=' + origin;
    });

    $(".album-details form").submit(function() {
        var albums = [];
        $("#archive-gallery li.album.selected").each(function() {
            albums.push($(this).attr('data-id'));
        });
        $(this).children("input[name='albums']").val(JSON.stringify(albums));
    });

    function toggleMultiedit() {
        var albums = $("#archive-gallery li.album.selected").length > 0;
        var images = $("#archive-gallery li.image.selected").length > 0;
        actionButtons.find("button.details, button.delete").hide();
        if(albums && images) {
            actionButtons.find("button.details.dummy").show();
            actionButtons.find("button.delete.both").show();
            $("div.delete-dialog p").hide().filter(".both").show();
        } else if(albums) {
            actionButtons.find("button.details.albums").show();
            actionButtons.find("button.delete.albums").show();
            $("div.delete-dialog p").hide().filter(".albums").show();
        } else if(images) {
            actionButtons.find("button.details.images").show();
            actionButtons.find("button.delete.images").show();
            $("div.delete-dialog p").hide().filter(".images").show();
        } else {
            actionButtons.find("button.details.dummy").show();
            actionButtons.find("button.delete.dummy").show();
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
