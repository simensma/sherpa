/* Changing destination album */

var AlbumPicker = function(picked) {
    var that = this;
    this.picker = $("div.dialog.album-picker");
    this.picked = picked;
    this.current = {};

    this.picker.on('click', "a[data-albumpicker-id]", function() {
        that.cd($(this).attr('data-albumpicker-id'));
    });

    this.picker.find("button.pick").click(function() {
        that.picked(that.current);
        that.picker.dialog('close');
    });
}

AlbumPicker.prototype.cd = function(album_id) {
    var that = this;
    var ajaxloader = that.picker.find("img.ajaxloader");
    var path = that.picker.find("div.albumpath span.path");
    var children = that.picker.find("div.children");
    path.empty();
    children.empty();
    ajaxloader.show();
    var url = album_id;
    if(url != '') {
        url += '/';
    }

    $.ajaxQueue({
        url: '/sherpa/bildearkiv/innhold/album/' + url,
    }).done(function(result) {
        result = JSON.parse(result);

        // Set current to that one
        var name;
        if(result.path.length > 0) {
            name = result.path[result.path.length-1].name;
        } else {
            name = "Bildearkiv";
        }
        that.current = {
            id: album_id,
            name: name
        };

        // Re-enter path
        for(var i=0; i<result.path.length; i++) {
            path.append(' / <a href="javascript:undefined" data-albumpicker-id="' + result.path[i].id + '">' + result.path[i].name + '</a>');
        }

        // Apply album children
        for(var i=0; i<result.albums.length; i++) {
            var clone = $("div.dummy-child").clone();
            clone.removeClass('dummy-child').addClass('child');
            clone.find("a").text(result.albums[i].name).attr('data-albumpicker-id', result.albums[i].id);
            children.append(clone);
            clone.show();
        }
        if(result.albums.length == 0) {
            children.append('<p>Ingen underalbum i dette albumet. Klikk "Velg dette albumet" over hvis du vil velge dette albumet.</p>');
        }
    }).fail(function(result) {
        // Todo
    }).always(function(result) {
        ajaxloader.hide();
    });
}
