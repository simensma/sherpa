var archiveCallback;

$(document).ready(function() {

    showFolder('');

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
});

function chooseImagefromArchive(callback){
    archiveCallback = callback;
    $("div.image-archive-picker").modal();
}

function hideContent() {
    $("div.image-archive-picker div.too-few-chars").hide();
    var content = $("div.image-archive-picker div.content");
    content.empty();
    var ajaxLoader = $('<img class="ajaxloader" src="/static/img/ajax-loader-small.gif" alt="Laster, vennligst vent...">');
    content.append(ajaxLoader);
    return ajaxLoader;
}

function search(phrase) {
    var ajaxLoader = hideContent();
    $.ajax({
        url: $("div.image-archive-picker").attr("data-search-url"),
        data: { query: phrase }
    }).done(function(result) {
        result = JSON.parse(result);
        $("div.image-archive-picker div.content").append(result.html);
    }).fail(function(result) {
        // Todo
    }).always(function(result) {
        ajaxLoader.remove();
    });
}

function showFolder(album) {
    var ajaxLoader = hideContent();
    $.ajax({
        url: $("div.image-archive-picker").attr("data-album-url"),
        data: { album: album }
    }).done(function(result) {
        result = JSON.parse(result);
        $("div.image-archive-picker div.content").append(result.html);
    }).fail(function(result) {
        // Todo
    }).always(function(result) {
        ajaxLoader.remove();
    });
}

$(document).on('click', 'div.image-archive-picker a.clickable-album', function() {
    showFolder($(this).attr('data-id'));
});

$(document).on('click', 'div.image-archive-picker img.clickable-image', function() {
    var url = "http://cdn.turistforeningen.no/images/" + $(this).attr('data-path');
    var description = $(this).attr('data-description');
    var photographer = $(this).attr('data-photographer');

    $("div.image-archive-picker").modal('hide');
    archiveCallback(url.trim(), description.trim(), photographer.trim());
});
