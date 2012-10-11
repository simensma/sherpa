$(document).ready(function() {

    var actionButtons = $("div.imagearchive-action-buttons");

    actionButtons.find("button.upload").click(function() {
        window.location = $(this).attr('data-href');
    });
    actionButtons.find("button.albums.details").click(function() {
        $(".album-details.dialog").dialog('open');
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
        actionButtons.find("button.details").hide();
        if(albums && images) {
            actionButtons.find("button.details.dummy").show();
            $("div.delete-dialog p").hide().filter(".both").show();
            actionButtons.find("button.delete").removeAttr('disabled').html('<i class="icon-remove"></i> Slett album og bilder');
        } else if(albums) {
            $("div.delete-dialog p").hide().filter(".albums").show();
            actionButtons.find("button.details.albums").show();
            actionButtons.find("button.delete").removeAttr('disabled').html('<i class="icon-remove"></i> Slett album');
        } else if(images) {
            $("div.delete-dialog p").hide().filter(".images").show();
            actionButtons.find("button.details.images").show();
            actionButtons.find("button.delete").removeAttr('disabled').html('<i class="icon-remove"></i> Slett bilder');
        } else {
            actionButtons.find("button.delete").attr('disabled', true);
            actionButtons.find("button.details.dummy").show();
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
