$(document).ready(function() {
    var wrapper = $("div.memberid-sms");
    var button = wrapper.find("button");
    var input = wrapper.find("input[name='phone_mobile']");
    var loader = wrapper.find("img.ajaxloader");
    var results = wrapper.find("div.results").children();
    var ok = results.filter("div.alert.ok");
    var no_match = results.filter("div.alert.no-match");
    var error = results.filter("div.alert.error");
    var too_high_frequency = results.filter("div.too-high-frequency");

    input.keyup(function(e) {
        if(e.which == 13) { // Enter
            button.click();
        }
    });

    button.click(function() {
        button.hide();
        results.hide();
        loader.show();

        $.ajaxQueue({
            url: button.attr('data-href'),
            data: { phone_mobile: input.val() }
        }).done(function(result) {
            result = JSON.parse(result);
            results.find("span.number").text(input.val());
            if(result.status == 'ok') {
                ok.show();
                input.val(''); // Clear the input, so clicking 'OK' again isn't that tempting.
            } else if(result.status == 'service_fail') {
                error.show();
            } else if(result.status == 'connection_error') {
                error.show();
            } else if(result.status == 'no_match') {
                no_match.show();
            } else if(result.status == 'too_high_frequency') {
                too_high_frequency.show();
            }
        }).fail(function(result) {
            error.show();
        }).always(function(result) {
            button.show();
            loader.hide();
        });
    });
});
