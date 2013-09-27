$(document).ready(function() {

    var result = $("div.enrollment-result");
    var button = result.find("button.phone-receipt");
    var choose_user = result.find("div.choose-user");

    button.click(function() {
        $(this).prop('disabled', true);
        $(this).text("Sender, vennligst vent...");
        var button = $(this);
        var index = $(this).attr('data-index');
        var number = $(this).attr('data-number');
        var memberserviceBackup = 'Dersom du/dere har planlagt å dra på tur i nærmeste fremtid, og ikke rekker å vente på at medlemskortet ankommer, kan dere kontakte medlemsservice for å få tilsendt kvittering på SMS.';
        $.ajaxQueue({
            url: button.attr('data-sms-url'),
            data: { index: index }
        }).done(function(result) {
            result = JSON.parse(result);
            if(result.error == 'none') {
                button.after('<p class="receipt-success">Kvittering har blitt sendt på SMS til ' + number + '.</p>');
                button.remove();
            } else if(result.error == 'foreign_number') {
                button.after('<p class="receipt-error">En teknisk feil har oppstått ved utsendelse av SMS. ' + memberserviceBackup + '</p>');
                button.remove();
            } else if(result.error == 'enrollment_uncompleted') {
                button.after('<p class="receipt-error">En teknisk feil har oppstått ved utsendelse av SMS. ' + memberserviceBackup + '</p>');
                button.remove();
            } else if(result.error == 'already_sent') {
                button.after('<p class="receipt-error">SMS-Kvittering har allerede blitt sendt til dette nummeret. Ta kontakt med medlemsservice dersom du mener dette er feil.</p>');
                button.remove();
            } else if(result.error == 'connection_error') {
                button.after('<p class="receipt-error">En teknisk feil har oppstått ved kontakt med vår SMS-leverandør. ' + memberserviceBackup + '</p>');
                button.remove();
            } else if(result.error == 'service_fail') {
                button.after('<p class="receipt-error">En teknisk feil har oppstått ved kontakt med vår SMS-leverandør. ' + memberserviceBackup + '</p>');
                button.remove();
            }
        }).fail(function(result) {
            button.after('<p class="receipt-error">En teknisk feil har oppstått ved utsendelse av SMS. ' + memberserviceBackup + '</p>');
            button.remove();
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
