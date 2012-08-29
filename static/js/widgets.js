/* JS for widgets */

$(document).ready(function() {

    //Promo-box
    $("div.widget.promo div.menu li").click(function() {
        if($(this).children("a").length > 0) {
            window.location = $(this).children("a").attr('href');
        }
    });

    /* Display/hide services menu for small screens */
    $("div.widget.promo p.display-promo-menu a").click(function() {
        $("div.widget.promo div.menu").toggle('slow');
        var icon = $(this).find("i");
        var clazz = icon.get(0).className;
        icon.addClass(icon.attr('data-toggle')).removeClass(clazz).attr('data-toggle', clazz);
    });

    //carousel, stop spinning
    $('.carousel').each(function(){
        $(this).carousel({
            interval:false
        });
    });

});
