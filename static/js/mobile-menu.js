$(function() {

    var header = $('header');
    var main_menu = header.find('nav#menus');
    var core_menu = $('.widget.promo, .widget.campaign').find('.menu');
    var search_form = header.find('form.search-mobile');

    var menu_button = header.find('.mobile-control .display-menu a');
    var search_button = header.find('.display-search a');

    menu_button.click(function() {
        main_menu.slideToggle('slow');
        core_menu.slideToggle('slow');
        search_form.slideUp('slow');
    });

    search_button.click(function() {
        main_menu.slideUp('slow');
        core_menu.slideUp('slow');
        search_form.slideToggle('slow');
    });

});
