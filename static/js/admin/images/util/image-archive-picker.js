var bcList;
var bcRoot = $('<li><a href="javascript:undefined">Bildearkiv</a></li>');

var archiveCallback;

$(document).ready(function() {

    bcList = $("div.image-archive-picker div#imagearchive ul.breadcrumb");
    showFolder('');
    $("div.image-archive-picker div.too-few-chars").hide();
    $("div.image-archive-picker div.empty-src").hide();

    $("div.image-archive-picker button.cancel-chooser").click(function() {
        $("div.image-archive-picker").modal('hide');
    });

    $("div.image-archive-picker button.image-search").click(doSearch);
    $("div.image-archive-picker input[name='search']").keydown(function(e) {
        if(e.which == 13) { // Enter
            doSearch();
        }
    });

    function doSearch() {
        var query = $("div.image-archive-picker input[name='search']").val();
        if(query.length < IMAGE_SEARCH_LENGTH) {
            $("div.image-archive-picker div.too-few-chars").show();
        } else {
            search(query);
        }
    }

    $("div.image-details input[name='photographer']").typeahead({
        minLength: 3,
        source: function(query, process) {
            $.ajaxQueue({
                url: '/sherpa/bildearkiv/fotograf/',
                data: { name: query }
            }).done(function(result) {
                process(JSON.parse(result));
            });
        }
    });
});

function chooseImagefromArchive(callback){
    archiveCallback = callback;
    $("div.image-archive-picker").modal();
}

function hideContent() {
    $("div.image-archive-picker div.too-few-chars").hide();
    $("div.image-archive-picker div#imagearchive ul#images").children().remove();
    var ajaxLoader = $('<img class="ajaxloader" src="/static/img/ajax-loader-small.gif" alt="Laster, vennligst vent...">');
    var list = $("div.image-archive-picker div#imagearchive div#contentlist");
    list.contents().remove();
    list.append(ajaxLoader);
    return ajaxLoader;
}

function search(phrase) {
    var ajaxLoader = hideContent();
    $.ajax({
        url: '/sherpa/bildearkiv/søk/json/',
        data: { query: phrase }
    }).done(function(result) {
        result = JSON.parse(result);
        updateContents(result.parents, result.albums, result.images,
            '<strong>Beklager!</strong><br>Vi fant ingen bilder tilsvarende søket ditt :-(');
    }).fail(function(result) {
        // Todo
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
        // Todo
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
        var item = $('<div class="album"><a href="javascript:undefined" data-id="' + albums[i].id + '/"><img src="/static/img/icons/imagearchive/folder.png" alt="Album" class="album"> ' + albums[i].name + '</a></div><div style="clear: both;"></div>');
        item.find("a").click(function() {
            showFolder($(this).attr('data-id'));
        });
        $("div.image-archive-picker div#imagearchive div#contentlist").append(item);
    }

    // Add images
    for(var i=0; i<images.length; i++) {
        var item = $('<li data-path="' + images[i].key + '.' + images[i].extension + '" data-description="' + images[i].description + '" data-photographer="' + images[i].photographer + '"><p><img src="http://cdn.turistforeningen.no/images/' + images[i].key + '-150.' + images[i].extension + '" alt="Thumbnail"></p>' + images[i].width + ' x ' + images[i].height + '<br>' + images[i].photographer + '</li>');
        item.click(function() {

            var url = "http://cdn.turistforeningen.no/images/" + $(this).attr('data-path');
            var description = $(this).attr('data-description');
            var photographer = $(this).attr('data-photographer');

            $("div.image-archive-picker").modal('hide');
            archiveCallback(url.trim(), description.trim(), photographer.trim());
        });
        $("div.image-archive-picker div#imagearchive ul#images").append(item);
    }

    // No albums and no images
    if(albums.length == 0 && images.length == 0) {
        var sorry = $('<div class="alert alert-info span4"><a class="close">x</a>' + emptyText + '</div>');
        sorry.find("a").click(function() { $(this).parent().remove(); });
        $("div.image-archive-picker div#imagearchive div#contentlist").append(sorry);
    }
}
