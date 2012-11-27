$(document).ready(function() {

    /* Restore password */
    $("div#forgot-password").hide();
    $("div#login a.forgot").click(function() {
        $(this).hide();
        $("div#forgot-password").slideDown();
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
    new MobileMenu(
        $("header div.mobile-control"),
        $("header nav#menus"),
        $("div.widget.promo div.menu"),
        $("header form.search-mobile"));
});

var MobileMenu = function(control, mainMenu, widgetMenu, search) {
    var self = this;
    this.menuButton = control.find("p.display-menu a");
    this.mainMenu = mainMenu;
    this.widgetMenu = widgetMenu;
    this.search = search;
    this.searchButton = control.find("p.display-search a");

    this.menuButton.click(function() {
        self.mainMenu.toggle('slow');
        self.widgetMenu.toggle('slow');
        self.search.hide('slow');
    });

    this.searchButton.click(function() {
        self.mainMenu.hide('slow');
        self.widgetMenu.hide('slow');
        self.search.toggle('slow');
    });
}
