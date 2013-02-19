$(document).ready(function() {

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
        self.mainMenu.slideToggle('slow');
        self.widgetMenu.slideToggle('slow');
        self.search.slideUp('slow');
    });

    this.searchButton.click(function() {
        self.mainMenu.slideUp('slow');
        self.widgetMenu.slideUp('slow');
        self.search.slideToggle('slow');
    });
};
