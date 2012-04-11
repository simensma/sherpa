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
    });

});

function showFolder(album) {
    var list = $("div#dialog-change-image div#imagearchive div#contentlist");
    list.contents().remove();
    list.append('<img class="ajaxloader" src="/static/img/ajax-loader-small.gif" alt="Laster, vennligst vent...">');
    $.ajax({
        url: '/sherpa/bildearkiv/innhold/' + album,
        type: 'POST'
    }).done(function(result) {
        result = JSON.parse(result);

        // Add albums
        for(var i=0; i<result.albums.length; i++) {
            var item = $('<div class="album"><a href="javascript:undefined" data-id="' + result.albums[i].id + '/"><img src="/static/img/icons/folder.png" alt="Album" class="album"> ' + result.albums[i].name + '</a></div><div style="clear: both;"></div>');
            item.find("a").click(function() {
                showFolder($(this).attr('data-id'));
            });
            $("div#dialog-change-image div#imagearchive div#contentlist").append(item);
        }

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
    }).fail(function(result) {
        $(document.body).html(result.responseText);
    }).always(function(result) {
        list.find("img.ajaxloader").remove();
    });
}
