/* Membership */

$(document).ready(function() {

    $("table.prices img[data-popover]").hover(function() {
        $(this).attr('src', '/static/img/icons/glyph/red/glyphicons_195_circle_info.png');
    }, function() {
        $(this).attr('src', '/static/img/icons/glyph/original/glyphicons_195_circle_info.png');
    });

    $("div#faq dl dd").hide();
    $("div#faq dl dt").click(function() {
        $(this).next().toggle();
    });

});
