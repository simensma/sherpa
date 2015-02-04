/* JS for widgets */

$(function() {

    Widgets.runIfExists('gallery', $("div.widget.gallery"));
    Widgets.runIfExists('articles', $("div.widget.articles"));
    Widgets.runIfExists('campaign', $("div.widget.campaign"), true);
    // Note that there's no need to run the aktivitet_listing widget

});

(function(Widgets, $, undefined) {

    /**
     * Run widget script if it exists in the current DOM
     * @param {bool} exclude_admin set to true if this script should NOT run when the widget is rendered in the
     *   admin layout.
     */
    Widgets.runIfExists = function(type, $widget, exclude_admin) {
        if($widget.length > 0 && (!exclude_admin || $widget.attr('data-admin-context') === undefined)) {
            $widget.each(function(index, widget_element) {
                Widgets.run(type, $(widget_element));
            });
        }
    };

    Widgets.run = function(type, $widget) {
        if(type === 'gallery') {

            var $album_view = $widget.find('.album').first();
            var $carousel_view = $widget.find('.carousel').first();

            // Turn off auto slide
            $carousel_view.carousel({
                interval: false
            });

            // Add swipe events
            $carousel_view.find('.carousel-inner').swipe({
                swipeLeft: function() {
                    $carousel_view.carousel('next');
                },
                swipeRight: function() {
                    $carousel_view.carousel('prev');
                },
                // Default threshold is 75px
                threshold: 15,
            });

            // When in album view, click thumbnail to open full size view in carousel
            $widget.find('.album .item a').click(function (e) {
                $album_view.hide();

                var image_index = $(this).parents('.item').first().index();
                $widget.carousel(image_index);
                $carousel_view.show();
            });

            $('[data-toggle="tooltip"]').tooltip();

            // When in carousel view, go to album view by clicking switch view button
            $widget.find('.carousel .switch-view button').on('click', function () {
                $album_view.show();
                $carousel_view.hide();
            });

        } else if(type === 'articles') {

            // Articles (horizontal layout)
            imagesLoaded($widget, function() {
                // Adjust the contained image so it's centered within its fixed-height container
                $widget.find("div.horizontal div.image-container").each(function() {
                    var width = $(this).width();
                    var height = Math.round((width / 4) * 3);
                    $(this).css('height', height);

                    var $image = $(this).find("img");
                    if($image.width() / $image.height() <= 4/3) {
                        // Image width fits 4:3, just offset the top so that the height is fixed
                        $image.css('width', '100%');
                        var top_offset = (($image.height() - height) / 2) * -1;
                        $image.css('top', top_offset + 'px');
                    } else {
                        // Image is too wide for 4:3, it would be shorter than the intended height.
                        // Force the height, calculate the width by its original ratio and offset it accordingly
                        $image.css('height', height);
                        var new_image_width = (height / $image.height()) * $image.width();
                        $image.css('width', new_image_width);
                        var right_offset = ((new_image_width - width) / 2) * -1;
                        $image.css('right', right_offset + 'px');
                    }

                });

                // Set the height for news without images; we don't want these to be used but in case they are,
                // we'll handle it as gracefully as possible
                $widget.find("div.horizontal div.image-placeholder").each(function() {
                    var width = $(this).width();
                    var height = Math.round((width / 4) * 3);
                    $(this).css('height', height);
                });
            });

        } else if(type === 'campaign') {

            // Google Analytics isn't available on all sites; the UA needs to be configured
            if(typeof(_gaq) === 'undefined') {
                return;
            }

            // Track campaign views and clicks
            _gaq.push(['_trackEvent', 'Kampanje', 'Visning', $widget.find('.campaign').attr('data-dnt-ga-event-label')]);
            var campaign_button = $widget.find('[data-dnt-container="button"] a');
            if(campaign_button.length > 0) {
                campaign_button.click(function() {
                    _gaq.push(['_trackEvent', 'Kampanje', 'Klikk', $widget.find('.campaign').attr('data-dnt-ga-event-label')]);
                });
            }

            // Scale down large font sizes
            var FONT_SIZE_LIMIT = 32;
            $widget.find('.text').each(function() {
                var font_size = $(this).css('font-size');
                font_size = Number(font_size.substring(0, font_size.length - 2));
                if(font_size > FONT_SIZE_LIMIT) {
                    $(this).addClass('font-size-limit-exceeded');
                }
            });

        } else if(type === 'aktivitet_listing') {

            // Make sure the media query has been executed. This works automatically on the public pages and is only
            // used in the admin UI when inserting a new instance of this widget.
            new ElementQueries().update();

        }
    };

}(window.Widgets = window.Widgets || {}, jQuery ));
