/**
 * Picking a URL for an image
 */

var bcList;
var bcRoot = $('<li><a href="javascript:undefined">Bildearkiv</a></li>');

$(document).ready(function() {

    bcList = $("div#dialog-change-image div#imagearchive ul.breadcrumb");
    showFolder('');

    $("div#dialog-change-image button.insert-image").click(function() {
        var dialog = $(this).parents("div#dialog-change-image")
        dialog.dialog('close');
        currentImage.attr('src', dialog.find("input[name='url']").val());
        currentImage.attr('alt', dialog.find("input[name='alt']").val());
        $("#toolbar .save button.save").click();
    });

    function doSearch() {
        search($("div#dialog-change-image input[name='search']").val());
    }
    $("div#dialog-change-image button.image-search").click(doSearch);
    $("div#dialog-change-image input[name='search']").keydown(function(e) {
        if(e.which == 13) {
            // 13 is the Enter key
            doSearch();
        }
    });

});

function hideContent() {
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
    }).done(updateContents).fail(function(result) {
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
    }).done(updateContents).fail(function(result) {
        $(document.body).html(result.responseText);
    }).always(function(result) {
        ajaxLoader.remove();
    });
}

function updateContents(result) {
    result = JSON.parse(result);

    // Add breadcrumbs
    bcList.children().remove();
    bcList.append(bcRoot);
    bcRoot.find("a").click(function() {
        showFolder('');
    });
    for(var i=0; i<result.parents.length; i++) {
        var item = $('<li><a href="javascript:undefined" data-id="' + result.parents[i].id + '/">' + result.parents[i].name + '</a></li>');
        item.find("a").click(function() {
            showFolder($(this).attr('data-id'));
        });
        bcList.append($('<span class="divider">→</span>')).append(item);
    }

    // Add albums
    for(var i=0; i<result.albums.length; i++) {
        var item = $('<div class="album"><a href="javascript:undefined" data-id="' + result.albums[i].id + '/"><img src="/static/img/icons/folder.png" alt="Album" class="album"> ' + result.albums[i].name + '</a></div><div style="clear: both;"></div>');
        item.find("a").click(function() {
            showFolder($(this).attr('data-id'));
        });
        $("div#dialog-change-image div#imagearchive div#contentlist").append(item);
    }

    // Add images
    for(var i=0; i<result.images.length; i++) {
        var item = $('<li data-path="' + result.images[i].key + '.' + result.images[i].extension + '" data-description="' + result.images[i].description + '"><p><img src="http://cdn.turistforeningen.no/images/' + result.images[i].key + '-150.' + result.images[i].extension + '" alt="Thumbnail"></p>' + result.images[i].width + ' x ' + result.images[i].height + '<br>' + result.images[i].photographer + '</li>');
        item.click(function() {
            $("div#dialog-change-image input[name='url']").val("http://cdn.turistforeningen.no/images/" + $(this).attr('data-path'));
            $("div#dialog-change-image input[name='alt']").val($(this).attr('data-description'));
            $("div#dialog-change-image button.insert-image").click();
        });
        $("div#dialog-change-image div#imagearchive ul#images").append(item);
    }
}
