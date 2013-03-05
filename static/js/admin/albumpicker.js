/* Changing destination album */

$(document).ready(function() {
    (function(AlbumPicker, $, undefined ) {

        var picker = $("div.dialog.album-picker");
        var current = {};
        var allow_root = true;

        // Callback when an album has been picked
        var picked = function() {};

        picker.on('click', "a[data-albumpicker-id]", function() {
            setAlbum($(this).attr('data-albumpicker-id'));
        });

        picker.find("button.pick").click(function() {
            picker.dialog('close');
            picked(current);
        });

        picker.find("button.deselect").click(function() {
            current = {
                id: '',
                name: ''
            };
            picker.find("button.pick").click();
        });

        picker.find("button.cancel").click(function() {
            picker.dialog('close');
        });

        AlbumPicker.open = function(options) {
            setAlbum(options.album_id);
            allow_root = options.allow_root;
            if(options.allow_deselect) {
                picker.find("button.deselect").show();
            } else {
                picker.find("button.deselect").hide();
            }
            picked = options.picked;
            picker.dialog('open');
        }

        // Not using a form, so simulate search submit upon enter keypress in input
        picker.find("input[name='search']").keyup(function(e) {
            if(e.which == 13) {
                picker.find("button.search").click();
            }
        });

        picker.find("button.search").click(function() {
            search();
        });

        function setAlbum(album_id) {
            var ajaxloader = picker.find("img.ajaxloader");
            var path = picker.find("div.albumpath span.path");
            var children = picker.find("div.children");
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
                if(!allow_root && result.path.length == 0) {
                    picker.find("button.pick").attr('disabled', true);
                } else {
                    picker.find("button.pick").removeAttr('disabled');
                    var name;
                    if(result.path.length > 0) {
                        name = result.path[result.path.length-1].name;
                    } else {
                        name = "Bildearkiv";
                    }
                    current = {
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

        function search() {
            var ajaxloader = picker.find("img.ajaxloader");
            var children = picker.find("div.children");
            children.empty();
            ajaxloader.show();
            var query = picker.find("input[name='search']").val();
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
                data: { query: query }
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


    }(window.AlbumPicker = window.AlbumPicker || {}, jQuery ));
});
