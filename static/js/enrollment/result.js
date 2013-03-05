$(document).ready(function() {

    $("button.phone-receipt").click(function() {
        $(this).attr('disabled', true);
        $(this).text("Sender, vennligst vent...");
        var button = $(this);
        var index = $(this).attr('data-index');
        var number = $(this).attr('data-number');
        $.ajax({
            url: '/innmelding/sms/',
            data: { index: index }
        }).done(function(result) {
            result = JSON.parse(result);
            var memberserviceBackup = 'Dersom du/dere har planlagt å dra på tur i nærmeste fremtid, og ikke rekker å vente på at medlemskortet ankommer, kan dere kontakte medlemsservice for å få tilsendt kvittering på SMS.';
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
                button.after('<p class="receipt-error">En teknisk feil har oppstått ved kontakt med vår SMS-leverandør. Feilmelding oppgitt er:</p><pre>' + result.message + '</pre><p class="receipt-error">' + memberserviceBackup + '</p>');
                button.remove();
            }
        }).fail(function(result) {
            // Todo
        });
    });

});
