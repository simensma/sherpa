/* JS for widgets */

$(document).ready(function() {

    /* Promo-box */

    $("div.widget.promo div.menu li").click(function() {
        window.location = $(this).children("a").attr('href');
    });
});
