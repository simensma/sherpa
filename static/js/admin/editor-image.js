/**
 * Picking a URL for an image
 */

// Require this many characters for an image search (this is duplicated server-side)
var MIN_QUERY_LENGTH = 3;

var bcList;
var bcRoot = $('<li><a href="javascript:undefined">Bildearkiv</a></li>');

$(document).ready(function() {

    bcList = $("div#dialog-change-image div#imagearchive ul.breadcrumb");
    showFolder('');
    $("div#dialog-change-image div.too-few-chars").hide();
    $("div#dialog-change-image div.empty-url").hide();

    $("div#dialog-change-image button.insert-image").click(function() {
        var dialog = $(this).parents("div#dialog-change-image");
        var url = dialog.find("input[name='url']").val();
        if(url == "") {
            $("div#dialog-change-image div.empty-url").show();
            return;
        }
        $("div#dialog-change-image div.empty-url").hide();
        dialog.dialog('close');
        currentImage.attr('src', url);
        currentImage.attr('alt', dialog.find("input[name='alt']").val());
        var anchor = dialog.find("input[name='anchor']").val();
        if(anchor.length == 0) {
            // No link
            if(currentImage.parent("a").length > 0) {
                // *Was* link, but is now removed
                currentImage.parent().before(currentImage).remove();
            }
        } else {
            // Add link
            if(!anchor.match(/^https?:\/\//)) {
                anchor = "http://" + anchor;
            }
            if(currentImage.parent("a").length > 0) {
                // Link exists, update it
                currentImage.parent().attr('href', anchor);
            } else {
                // No existing link, add it
                var anchorEl = $('<a href="' + anchor + '"></a>');
                currentImage.before(anchorEl).detach();
                anchorEl.prepend(currentImage);
            }
        }
        $("#toolbar .save button.save").click();
    });

    $("div#dialog-change-image button.image-search").click(doSearch);
    $("div#dialog-change-image input[name='search']").keydown(function(e) {
        if(e.which == 13) {
            // 13 is the Enter key
            doSearch();
        }
    });
    function doSearch() {
        var query = $("div#dialog-change-image input[name='search']").val();
        if(query.length < MIN_QUERY_LENGTH) {
            $("div#dialog-change-image div.too-few-chars").show();
        } else {
            search(query);
        }
    }

});

function hideContent() {
    $("div#dialog-change-image div.too-few-chars").hide();
    $("div#dialog-change-image div#imagearchive ul#images").children().remove();
    var ajaxLoader = $('<img class="ajaxloader" src="/static/img/ajax-loader-small.gif" alt="Laster, vennligst vent...">');
    var list = $("div#dialog-change-image div#imagearchive div#contentlist");
    list.contents().remove();
    list.append(ajaxLoader);
    return ajaxLoader;
}

function search(phrase) {
    var ajaxLoader = hideContent();
    $.ajax({
        url: '/sherpa/bildearkiv/søk/',
        type: 'POST',
        data: "query=" + encodeURIComponent(phrase)
    }).done(function(result) {
        result = JSON.parse(result);
        updateContents(result.parents, result.albums, result.images,
            '<strong>Beklager!</strong><br>Vi fant ingen bilder tilsvarende søket ditt :-(');
    }).fail(function(result) {
        $(document.body).html(result.responseText);
    }).always(function(result) {
        ajaxLoader.remove();
    });
}

function showFolder(album) {
    var ajaxLoader = hideContent();
    $.ajax({
        url: '/sherpa/bildearkiv/innhold/' + album,
        type: 'POST'
    }).done(function(result) {
        result = JSON.parse(result);
        updateContents(result.parents, result.albums, result.images,
            '<strong>Her var det tomt!</strong><br>Det er ingen album eller bilder i dette albumet.');
    }).fail(function(result) {
        $(document.body).html(result.responseText);
    }).always(function(result) {
        ajaxLoader.remove();
    });
}

function updateContents(parents, albums, images, emptyText) {
    // Add breadcrumbs
    bcList.children().remove();
    bcList.append(bcRoot);
    bcRoot.find("a").click(function() {
        showFolder('');
    });
    for(var i=0; i<parents.length; i++) {
        var item = $('<li><a href="javascript:undefined" data-id="' + parents[i].id + '/">' + parents[i].name + '</a></li>');
        item.find("a").click(function() {
            showFolder($(this).attr('data-id'));
        });
        bcList.append($('<span class="divider">→</span>')).append(item);
    }

    // Add albums
    for(var i=0; i<albums.length; i++) {
        var item = $('<div class="album"><a href="javascript:undefined" data-id="' + albums[i].id + '/"><img src="/static/img/icons/folder.png" alt="Album" class="album"> ' + albums[i].name + '</a></div><div style="clear: both;"></div>');
        item.find("a").click(function() {
            showFolder($(this).attr('data-id'));
        });
        $("div#dialog-change-image div#imagearchive div#contentlist").append(item);
    }

    // Add images
    for(var i=0; i<images.length; i++) {
        var item = $('<li data-path="' + images[i].key + '.' + images[i].extension + '" data-description="' + images[i].description + '"><p><img src="http://cdn.turistforeningen.no/images/' + images[i].key + '-150.' + images[i].extension + '" alt="Thumbnail"></p>' + images[i].width + ' x ' + images[i].height + '<br>' + images[i].photographer + '</li>');
        item.click(function() {
            $("div#dialog-change-image input[name='url']").val("http://cdn.turistforeningen.no/images/" + $(this).attr('data-path'));
            $("div#dialog-change-image input[name='alt']").val($(this).attr('data-description'));
            $("div#dialog-change-image button.insert-image").click();
        });
        $("div#dialog-change-image div#imagearchive ul#images").append(item);
    }

    // No albums and no images
    if(albums.length == 0 && images.length == 0) {
        var sorry = $('<div class="alert alert-info span4"><a class="close">x</a>' + emptyText + '</div>');
        sorry.find("a").click(function() { $(this).parent().remove(); });
        $("div#dialog-change-image div#imagearchive div#contentlist").append(sorry);
    }
}
