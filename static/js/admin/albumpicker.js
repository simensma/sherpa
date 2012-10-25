/* Changing destination album */

var AlbumPicker = function(allow_root, picked) {
    var that = this;
    this.allow_root = allow_root;
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

    // Not using a form, so simulate submit upon enter keypress
    this.picker.find("input[name='search']").keyup(function(e) {
        if(e.which == 13) {
            that.picker.find("button.search").click();
        }
    });

    this.picker.find("button.search").click(function() {
        that.search();
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
        if(!that.allow_root && result.path.length == 0) {
            that.picker.find("button.pick").attr('disabled', true);
        } else {
            that.picker.find("button.pick").removeAttr('disabled');
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
        }

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

AlbumPicker.prototype.search = function() {
    var that = this;
    var ajaxloader = that.picker.find("img.ajaxloader");
    var children = that.picker.find("div.children");
    children.empty();
    ajaxloader.show();
    var query = that.picker.find("input[name='search']").val();
    if(typeof image_search_length === 'undefined') {
        // A default in case it's missing, but please use the settings variable via js_globals
        image_search_length = 3;
    }
    if(query.length < image_search_length) {
        children.append('<p>Vennligst bruk minst ' + image_search_length + ' søketegn, ellers vil du få alt for mange treff.</p>');
        ajaxloader.hide();
    }

    $.ajaxQueue({
        url: '/sherpa/bildearkiv/innhold/album/søk/',
        data: 'query=' + encodeURIComponent(query)
    }).done(function(result) {
        result = JSON.parse(result);

        // Apply album children
        for(var i=0; i<result.items.length; i++) {
            var clone = $("div.dummy-child").clone();
            clone.removeClass('dummy-child').addClass('child');
            var a = clone.find("a").clone();
            clone.find("a").remove();
            for(var j=0; j<result.items[i].length; j++) {
                a.text(result.items[i][j].name).attr('data-albumpicker-id', result.items[i][j].id);
                clone.append(a);
                if(j < result.items[i].length - 1) {
                    clone.append(" / ")
                }
                a = a.clone();
            }
            children.append(clone);
            clone.show();
        }
        if(result.items.length == 0) {
            children.append('<p>Fant ingen album som inneholdt "' + query + '".</p>');
        }
    }).fail(function(result) {
        // Todo
    }).always(function(result) {
        ajaxloader.hide();
    });
}
