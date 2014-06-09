/* JS for widgets */

$(function() {

    Widgets.runIfExists('promo', $("div.widget.promo"));
    Widgets.runIfExists('carousel', $("div.widget.carousel"));
    Widgets.runIfExists('articles', $("div.widget.articles"));

});

(function(Widgets, $, undefined) {

    Widgets.runIfExists = function(type, widget) {
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
                var width = $(this).width();
                var height = Math.round((width / 4) * 3);
                $(this).css('height', height);

                var image = $(this).find("img");
                if(image.width() / image.height() <= 4/3) {
                    // Image width fits 4:3, just offset the top so that the height is fixed
                    image.css('width', '100%');
                    var top_offset = ((image.height() - height) / 2) * -1;
                    image.css('top', top_offset + 'px');
                } else {
                    // Image is too wide for 4:3, it would be shorter than the intended height.
                    // Force the height, calculate the width by its original ratio and offset it accordingly
                    image.css('height', height);
                    var new_image_width = (height / image.height()) * image.width();
                    image.css('width', new_image_width);
                    var right_offset = ((new_image_width - width) / 2) * -1;
                    image.css('right', right_offset + 'px');
                }

            });

            // Set the height for news without images; we don't want these to be used but in case they are,
            // we'll handle it as gracefully as possible
            widget.find("div.horizontal div.image-placeholder").each(function() {
                var width = $(this).width();
                var height = Math.round((width / 4) * 3);
                $(this).css('height', height);
            });
        }
    };

}(window.Widgets = window.Widgets || {}, jQuery ));
