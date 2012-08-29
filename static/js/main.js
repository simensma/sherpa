$(document).ready(function() {

    /* Restore password */
    $("div#forgot-password").hide();
    $("div#login a.forgot").click(function() {
        $(this).hide();
        $("div#forgot-password").show();
    });
    $("div#forgot-password input[name='email']").keyup(function(e) {
        if(e.which == 13) {
            // Enter
            $("div#forgot-password button.restore-password").click();
        }
    });
    $("div#forgot-password button.restore-password").click(function() {
        $("div#forgot-password p.info").removeClass('success').removeClass('failure').text("");
        $(this).attr('disabled', true);
        $(this).attr('data-original-text', $(this).text());
        $(this).text("Sender e-post...");
        var button = $(this);
        $.ajax({
            url: '/minside/gjenopprett-passord/e-post/',
            data: 'email=' + encodeURIComponent($("div#forgot-password input[name='email']").val())
        }).done(function(result) {
            result = JSON.parse(result);
            if(result.status == 'invalid_email') {
                var info = $("div#forgot-password p.info");
                info.addClass('failure');
                info.text("Denne e-postadressen er ikke registrert på noen av våre brukere.");
                button.removeAttr('disabled');
                button.text(button.attr('data-original-text'));
            } else if(result.status == 'success') {
                var info = $("div#forgot-password p.info");
                info.addClass('success');
                info.text("En e-post har blitt sendt til adressen du oppgav med ytterligere instruksjoner for å få gjenopprettet passordet.");
                info.siblings().hide();
            }
        }).fail(function(r) {
            $("p.info").addClass('failure');
            $("p.info").text("En teknisk feil oppstod! Vennligst prøv igjen, eller kontakt medlemsservice dersom feilen vedvarer.");
            button.removeAttr('disabled');
            button.text(button.attr('data-original-text'));
        });
    });

    $("div#restore-password input[type='password']").focusin(function() {
        $("div#restore-password input[type='password']").parents("td.control-group").removeClass('error');
        $("div#restore-password td.info").text("");
    });
    $("div#restore-password form").submit(function(e) {
        if($("div#restore-password input[name='password']").val() != $("div#restore-password input[name='password-duplicate']").val()) {
            $("div#restore-password input[type='password']").parents("td.control-group").addClass('error');
            $("div#restore-password td.info").text("Passordene er ikke like.");
            e.preventDefault();
        } else if($("div#restore-password input[name='password']").val().length < password_length) {
            $("div#restore-password td.info").text("Du må ha minst " + password_length + " tegn i passordet.");
            e.preventDefault();
        }
    });

    /* Display/hide main menu for small screens */
    $("p.display-menu a").click(function() {
        $("nav#menus, div.login").toggle('slow');
        var icon = $(this).find("i");
        var clazz = icon.get(0).className;
        icon.addClass(icon.attr('data-toggle')).removeClass(clazz).attr('data-toggle', clazz);

        if($("div.widget.promo").length > 0) {
            $("div.widget.promo div.menu").toggle('slow');
            var icon = $(this).find("i");
            var clazz = icon.get(0).className;
            icon.addClass(icon.attr('data-toggle')).removeClass(clazz).attr('data-toggle', clazz);
        }
    });


});
