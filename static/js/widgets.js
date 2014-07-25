/* JS for widgets */

$(function() {

    Widgets.runIfExists('carousel', $("div.widget.carousel"));
    Widgets.runIfExists('articles', $("div.widget.articles"));

});

(function(Widgets, $, undefined) {

    /**
     * Run widget script if it exists in the current DOM
     * @param {bool} exclude_admin set to true if this script should NOT run when the widget is rendered in the
     *   admin layout.
     */
    Widgets.runIfExists = function(type, widget, exclude_admin) {
        if(widget.length > 0 && (!exclude_admin || widget.attr('data-admin-context') === undefined)) {
            Widgets.run(type, widget);
        }
    };

    Widgets.run = function(type, widget) {
        if(type === 'carousel') {

            //carousel, stop spinning
            $(this).find("div.carousel").each(function() {
                $(this).carousel({
                    interval:false
                });
            });

        } else if(type === 'articles') {

            // Articles (horizontal layout)
            imagesLoaded(widget, function() {
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
            });
        }
    };

}(window.Widgets = window.Widgets || {}, jQuery ));
