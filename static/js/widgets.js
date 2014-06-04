/* JS for widgets */

$(function() {

    Widgets.runIfExists('promo', $("div.widget.promo"));
    Widgets.runIfExists('carousel', $("div.widget.carousel"));
    Widgets.runIfExists('articles', $("div.widget.articles"));

});

(function(Widgets, $, undefined) {

    Widgets.runIfExists = function(type, selector) {
        var widget = $(selector);
        if(widget.length > 0) {
            Widgets.run(type, widget);
        }
    };

    Widgets.run = function(type, widget) {
        if(type === 'promo') {

            //Promo-box
            $(this).find("div.menu.li").click(function() {
                if($(this).children("a").length > 0) {
                    window.location = $(this).children("a").attr('href');
                }
            });

        } else if(type === 'carousel') {

            //carousel, stop spinning
            $(this).find("div.carousel").each(function() {
                $(this).carousel({
                    interval:false
                });
            });

        } else if(type === 'articles') {

            // Articles (horizontal layout)
            // Adjust the contained image so it's centered within its fixed-height container
            widget.find("div.horizontal div.image-container").each(function() {
                var total_height = $(this).height();
                var image = $(this).find("img");
                var top_offset = ((image.height() - total_height) / 2) * -1;
                image.css('top', top_offset + 'px');
            });

        }
    };

}(window.Widgets = window.Widgets || {}, jQuery ));
