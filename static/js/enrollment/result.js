$(document).ready(function() {

    $("button.phone-receipt").click(function() {
        $(this).attr('disabled', true);
        $(this).text("Sender, vennligst vent...");
        var button = $(this);
        var index = $(this).attr('data-index');
        var number = $(this).attr('data-number');
        $.ajax({
            url: '/innmelding/sms/',
            type: 'POST',
            data: 'index=' + encodeURIComponent(index)
        }).done(function(result) {
            result = JSON.parse(result);
            if(result.error == 'none') {
                button.after('<p class="receipt-success">Kvittering har blitt sendt på SMS til ' + number + '.</p>');
                button.remove();
            } else if(result.error == 'foreign_number') {
                button.after('<p class="receipt-error">En teknisk feil har oppstått ved utsendelse av SMS. Vennligst kontakt medlemsservice for å motta SMS-kvittering.</p>');
                button.remove();
            } else if(result.error == 'not_registered') {
                button.after('<p class="receipt-error">En teknisk feil har oppstått ved utsendelse av SMS. Vennligst kontakt medlemsservice for å motta SMS-kvittering.</p>');
                button.remove();
            } else if(result.error == 'already_sent') {
                button.after('<p class="receipt-error">SMS-Kvittering har allerede blitt sendt til dette nummeret. Ta kontakt med medlemsservice dersom du mener dette er feil.</p>');
                button.remove();
            } else if(result.error == 'service_fail') {
                button.after('<p class="receipt-error">En teknisk feil har oppstått ved kontakt med vår SMS-leverandør. Feilmelding oppgitt er:</p><pre>' + result.message + '</pre><p class="receipt-error">Vennligst kontakt medlemsservice for å motta SMS-kvittering.</p>');
                button.remove();
            }
        }).fail(function(result) {
            $(document.body).html(result.responseText);
        });
    });

});
