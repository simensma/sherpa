$(document).ready(function() {

    var result = $("div.enrollment-result");
    var sms = result.find("p.sms");
    var choose_user = result.find("div.choose-user");

    sms.each(function() {
        var sms_anchor = $(this).find("a.phone-receipt");
        var sending = $(this).find("span.sending");
        sms_anchor.click(function() {
            sms_anchor.hide();
            sending.show();
            var index = $(this).attr('data-index');
            var number = $(this).attr('data-number');
            var memberserviceBackup = 'Dersom du/dere har planlagt å dra på tur i nærmeste fremtid, og ikke rekker å vente på at medlemskortet ankommer, kan dere kontakte medlemsservice for å få tilsendt kvittering på SMS.';
            $.ajaxQueue({
                url: sms_anchor.attr('data-sms-url'),
                data: { index: index }
            }).done(function(result) {
                result = JSON.parse(result);
                if(result.error == 'none') {
                    sending.after('<p class="receipt-success">Kvittering har blitt sendt på SMS til ' + number + '.</p>');
                    sending.remove();
                } else if(result.error == 'foreign_number') {
                    sending.after('<p class="receipt-error">En teknisk feil har oppstått ved utsendelse av SMS. ' + memberserviceBackup + '</p>');
                    sending.remove();
                } else if(result.error == 'enrollment_uncompleted') {
                    sending.after('<p class="receipt-error">En teknisk feil har oppstått ved utsendelse av SMS. ' + memberserviceBackup + '</p>');
                    sending.remove();
                } else if(result.error == 'already_sent') {
                    sending.after('<p class="receipt-error">SMS-Kvittering har allerede blitt sendt til dette nummeret. Ta kontakt med medlemsservice dersom du mener dette er feil.</p>');
                    sending.remove();
                } else if(result.error == 'connection_error') {
                    sending.after('<p class="receipt-error">En teknisk feil har oppstått ved kontakt med vår SMS-leverandør. ' + memberserviceBackup + '</p>');
                    sending.remove();
                } else if(result.error == 'service_fail') {
                    sending.after('<p class="receipt-error">En teknisk feil har oppstått ved kontakt med vår SMS-leverandør. ' + memberserviceBackup + '</p>');
                    sending.remove();
                }
            }).fail(function(result) {
                sending.after('<p class="receipt-error">En teknisk feil har oppstått ved utsendelse av SMS. ' + memberserviceBackup + '</p>');
                sending.remove();
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
