/**
 * Picking a URL for an image
 */

$(document).ready(function() {

    showFolder('');

});

function showFolder(album) {
    $("div#dialog-change-image div#imagearchive div#contentlist").contents().remove();
    $.ajax({
        url: '/sherpa/bildearkiv/innhold/' + album,
        type: 'POST'
    }).done(function(result) {
        result = JSON.parse(result);
        for(var i=0; i<result.albums.length; i++) {
            var item = $('<p><a href="javascript:undefined" data-id="' + result.albums[i].id + '/">Album: ' + result.albums[i].id + '/' + result.albums[i].name + '</a></p>')
            item.find("a").click(function() {
                showFolder($(this).attr('data-id'));
            });
            $("div#dialog-change-image div#imagearchive div#contentlist").append(item);
        }
    }).fail(function(result) {
        $(document.body).html(result.responseText);
    }).always(function(result) {
    });
}
