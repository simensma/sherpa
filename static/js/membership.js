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

    // Press button when enter is pressed in input
    $("input[name='zipcode']").keydown(function(e) {
        if(e.which == 13) {
            // 13 is the Enter key
            $("button.zipcode-search").click();
        }
    });

    $("button.zipcode-search").click(function() {
        var zipcode = $("input[name='zipcode']").val();
        if(zipcode == '') {
            $("div.zipcode-modal").find("h3, p").hide().filter('.missing').show();
            $("div.zipcode-modal").modal();
            return $(this);
        }
        $.ajax({
            url: '/medlem/postnummer/',
            data: 'zipcode=' + encodeURIComponent(zipcode)
        }).done(function(result) {
            result = JSON.parse(result);
            if(result.url !== undefined) {
                // Create and click an anchor instead of using window.location so that the browser includes the referer
                $('<a class="hide" href="' + result.url + '"></a>').appendTo(document.body).get(0).click();
            } else if(result.error == 'invalid_zipcode' || result.error == 'unregistered_zipcode') {
                $("strong.zipcode").text(result.zipcode);
                $("div.zipcode-modal").find("h3, p").hide().filter('.invalid').show();
                $("div.zipcode-modal").modal();
            }
        }).fail(function(result) {
            $("div.zipcode-modal").find("h3, p").hide().filter('.fail').show();
            $("div.zipcode-modal").modal();
        });
    });

});
