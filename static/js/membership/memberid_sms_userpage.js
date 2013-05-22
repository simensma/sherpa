$(document).ready(function() {
    var wrapper = $("div.memberid-sms");
    var number = wrapper.find("span.number").text();
    var trigger = wrapper.find("a.trigger");
    var sending = wrapper.find("span.sending");
    var missing_number = wrapper.find("span.missing-number");
    var ok = wrapper.find("span.ok");
    var no_match = wrapper.find("span.no-match");
    var error = wrapper.find("span.error");

    trigger.click(function() {
        trigger.hide();
        if(number.trim() === '') {
            missing_number.show();
            return $(this);
        }
        sending.show();
        $.ajaxQueue({
            url: trigger.attr('data-href')
        }).done(function(result) {
            result = JSON.parse(result);
            if(result.status == 'ok') {
                ok.show();
            } else if(result.status == 'service_fail') {
                error.show();
            } else if(result.status == 'missing_number') {
                // This shouldn't happen (we already checked 'number'), but handle it anyway
                missing_number.show();
            } else if(result.status == 'connection_error') {
                error.show();
            }
        }).fail(function(result) {
            error.show();
        }).always(function(result) {
            sending.hide();
        });
    });
});
