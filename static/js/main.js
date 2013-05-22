$(document).ready(function() {

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
