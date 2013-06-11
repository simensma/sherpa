/* Membership */

$(document).ready(function() {

    var zipcode_button = $("button.zipcode-search");

    $("div.benefits dl dd, div#faq dl dd").hide();
    $("div.benefits dl dt, div#faq dl dt").click(function() {
        $(this).next().slideToggle(400);
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
            zipcode_button.click();
        }
    });

    zipcode_button.click(function() {
        var loader = $(this).siblings('img.ajaxloader.zipcode-search');
        zipcode_button.prop('disabled', true);
        loader.show();
        var zipcode = $("input[name='zipcode']").val();
        if(zipcode === '') {
            $("div.zipcode-modal").find("h3, p").hide().filter('.missing').show();
            $("div.zipcode-modal").modal();
            zipcode_button.prop('disabled', false);
            loader.hide();
            return $(this);
        }
        $.ajaxQueue({
            url: zipcode_button.attr('data-zipcode-url'),
            data: { zipcode: zipcode }
        }).done(function(result) {
            result = JSON.parse(result);
            if(result.url !== undefined) {
                // Create and click an anchor instead of using window.location so that the browser includes the referer
                $('<a class="hide" href="' + result.url + '"></a>').appendTo(document.body).get(0).click();
            } else if(result.error == 'invalid_zipcode') {
                $("strong.zipcode").text(result.zipcode);
                $("div.zipcode-modal").find("h3, p").hide().filter('.invalid').show();
                $("div.zipcode-modal").modal();
                zipcode_button.prop('disabled', false);
                loader.hide();
            } else if(result.error == 'unregistered_zipcode') {
                $("strong.zipcode").text(result.zipcode);
                $("div.zipcode-modal").find("h3, p").hide().filter('.unregistered').show();
                $("div.zipcode-modal").modal();
                zipcode_button.prop('disabled', false);
                loader.hide();
            }
        }).fail(function(result) {
            $("div.zipcode-modal").find("h3, p").hide().filter('.fail').show();
            $("div.zipcode-modal").modal();
            zipcode_button.prop('disabled', false);
            loader.hide();
        });
    });

});
