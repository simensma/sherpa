$(document).ready(function() {

    /* Restore password */
    var forgot_password = $("div.forgot-password");
    $("div#login a.forgot").click(function() {
        $(this).parent().hide();
        forgot_password.slideDown();
    });
    forgot_password.find("input[name='email']").keyup(function(e) {
        if(e.which == 13) { // Enter
            forgot_password.find("button.restore-password").click();
        }
    });
    forgot_password.find("button.restore-password").click(function() {
        forgot_password.find("p.info").hide();
        var button = $(this);
        button.hide();
        $("img.ajaxloader").show();
        $.ajax({
            url: '/minside/gjenopprett-passord/e-post/',
            data: 'email=' + encodeURIComponent(forgot_password.find("input[name='email']").val())
        }).done(function(result) {
            result = JSON.parse(result);
            if(result.status == 'unknown_email') {
                forgot_password.find("p.info.unknown").show();
                button.show();
            } else if(result.status == 'invalid_email') {
                forgot_password.find("p.info.invalid").show();
                button.show();
            } else if(result.status == 'success') {
                forgot_password.find("p.info.success").show();
            }
        }).fail(function(r) {
            forgot_password.find("p.info.error").show();
            button.removeAttr('disabled');
            button.text(button.attr('data-original-text'));
        }).always(function(r) {
            $("img.ajaxloader").hide();
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
