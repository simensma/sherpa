/* Membership */

$(document).ready(function() {

    $("table.prices img[data-popover]").hover(function() {
        $(this).attr('src', '/static/img/icons/glyph/red/glyphicons_195_circle_info.png');
    }, function() {
        $(this).attr('src', '/static/img/icons/glyph/original/glyphicons_195_circle_info.png');
    });

    $("div#benefits dl dd, div#faq dl dd").hide();
    $("div#benefits dl dt, div#faq dl dt").click(function() {
        $(this).next().toggle(400);
    });

    var duration = 600;
    $("div#benefits").hide();
    $("div.benefits-toggle a.hider").hide();
    $("div.benefits-toggle-buttons div.hide-button").hide();
    $("div.benefits-toggle").click(function() {
        $("div#benefits").toggle(duration);
        $("div.benefits-toggle a.shower").toggle();
        $("div.benefits-toggle a.hider").toggle();
        $("div.benefits-toggle-buttons div.hide-button").toggle();
        $("div.benefits-toggle-buttons div.show-button").toggle();
    });

    $("div.benefits-large").hover(function() {
        $(this).find('.hover-content').fadeIn(200);
    }, function() {
        $(this).find('.hover-content').fadeOut(200);
    });

});
