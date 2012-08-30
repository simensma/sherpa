/* JS for widgets */

$(document).ready(function() {

    //Promo-box
    $("div.widget.promo div.menu li").click(function() {
        if($(this).children("a").length > 0) {
            window.location = $(this).children("a").attr('href');
        }
    });

    //carousel, stop spinning
    $('.carousel').each(function(){
        $(this).carousel({
            interval:false
        });
    });

});
