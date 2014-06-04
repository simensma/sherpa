/* JS for widgets */

$(function() {

    //Promo-box
    $("div.widget.promo div.menu li").click(function() {
        if($(this).children("a").length > 0) {
            window.location = $(this).children("a").attr('href');
        }
    });

    //carousel, stop spinning
    $("div.widget.carousel div.carousel").each(function() {
        $(this).carousel({
            interval:false
        });
    });

    // Articles (horizontal layout)
    // Adjust the contained image so it's centered within its fixed-height container
    $("div.widget.articles div.horizontal div.image-container").each(function() {
        var total_height = $(this).height();
        var image = $(this).find("img");
        var top_offset = ((image.height() - total_height) / 2) * -1;
        image.css('top', top_offset + 'px');
    });

});
