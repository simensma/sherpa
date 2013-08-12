$(document).ready(function() {

    var actionButtons = $("div.imagearchive-action-buttons");
    var modal_album_details = $("div.modal.album-details");
    var modal_album_add = $("div.modal.album-add");
    var modal_delete = $("div.modal.delete");

    actionButtons.find("button.albums.details").click(function() {
        modal_album_details.modal();
    });

    actionButtons.find("button.images.details").click(function() {
        var images = [];
        $("#archive-gallery li.image.selected").each(function() {
            images.push($(this).attr('data-id'));
        });
        window.location = '/sherpa/bildearkiv/bilde/oppdater/?bilder=' + encodeURIComponent(JSON.stringify(images)) + '&origin=' + origin;
    });

    actionButtons.find("button.move").click(function() {
        var album_id = $(this).parent().attr('data-album-id');
        var selected = getSelectedItems();
        AlbumPicker.open({
            album_id: album_id,
            allow_root: selected.images.length == 0,
            allow_deselect: selected.albums.length == 0,
            picked: function(album) {
                var form = $("form.move-items");
                form.find("input[name='albums']").val(JSON.stringify(selected.albums));
                form.find("input[name='images']").val(JSON.stringify(selected.images));
                form.find("input[name='destination_album']").val(album.id);
                form.submit();
            }
        });
    });

    actionButtons.find("button.album.add").click(function() {
        modal_album_add.modal();
    });

    actionButtons.find("button.delete").click(function() {
        modal_delete.modal();
    });

    modal_album_details.find("form").submit(function() {
        var albums = [];
        $("#archive-gallery li.album.selected").each(function() {
            albums.push($(this).attr('data-id'));
        });
        $(this).children("input[name='albums']").val(JSON.stringify(albums));
    });

    function toggleMultiedit() {
        var albums = $("#archive-gallery li.album.selected").length > 0;
        var images = $("#archive-gallery li.image.selected").length > 0;
        actionButtons.find("button.details, button.move, button.delete").hide();
        if(albums && images) {
            actionButtons.find("button.details.dummy").show();
            actionButtons.find("button.move.both").show();
            actionButtons.find("button.delete.both").show();
            modal_delete.find("p").hide().filter(".both").show();
        } else if(albums) {
            actionButtons.find("button.details.albums").show();
            actionButtons.find("button.move.albums").show();
            actionButtons.find("button.delete.albums").show();
            modal_delete.find("p").hide().filter(".albums").show();
        } else if(images) {
            actionButtons.find("button.details.images").show();
            actionButtons.find("button.move.images").show();
            actionButtons.find("button.delete.images").show();
            modal_delete.find("p").hide().filter(".images").show();
        } else {
            actionButtons.find("button.details.dummy").show();
            actionButtons.find("button.move.dummy").show();
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

    modal_delete.find("button").click(function() {
        modal_delete.modal('hide');
    });
    modal_delete.find("form").submit(function() {
        var selected = getSelectedItems();
        $(this).find("input[name='albums']").val(JSON.stringify(selected.albums));
        $(this).find("input[name='images']").val(JSON.stringify(selected.images));
    });

    function getSelectedItems() {
        var albums = [];
        var images = [];
        $("#archive-gallery li.album.selected").each(function() {
            albums.push($(this).attr('data-id'));
        });
        $("#archive-gallery li.image.selected").each(function() {
            images.push($(this).attr('data-id'));
        });
        return {
            albums: albums,
            images: images
        };
    }

});
