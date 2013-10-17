$(document).ready(function() {

    var result = $("div.enrollment-result");
    var sms = result.find("div.sms");
    var choose_user = result.find("div.choose-user");

    sms.each(function() {
        var sms_anchor = $(this).find("a.phone-receipt");
        var sending = $(this).find("p.sending");
        sms_anchor.click(function() {
            sms_anchor.hide();
            sending.show();
            var index = $(this).attr('data-index');
            var number = $(this).attr('data-number');
            $.ajaxQueue({
                url: sms_anchor.attr('data-sms-url'),
                data: { index: index }
            }).done(function(result) {
                result = JSON.parse(result);
                if(result.error == 'none') {
                    sms.find("p.success").show();
                } else if(result.error == 'foreign_number') {
                    sms.find("p.technical-error").show();
                } else if(result.error == 'enrollment_uncompleted') {
                    sms.find("p.technical-error").show();
                } else if(result.error == 'already_sent') {
                    sms.find("p.already-sent").show();
                } else if(result.error == 'connection_error') {
                    sms.find("p.connection-error").show();
                } else if(result.error == 'service_fail') {
                    sms.find("p.service-fail").show();
                }
            }).fail(function(result) {
                sms.find("p.technical-error").show();
            }).always(function(result) {
                sending.hide();
            });
        });
    });

    choose_user.find("input[name='user']").change(function() {
        choose_user.find("a.user").hide();
        choose_user.find("a.user[data-user-id='" + $(this).val() + "']").show();
    });

    choose_user.find("a[disabled]").click(function(e) {
        e.preventDefault();
    });

});
