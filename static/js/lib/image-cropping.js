(function(ImageCropper, $, undefined ) {

    /**
     * Scales and positions an image in its container such that it appears cropped
     * It is assumed that the container is positioned relatively and hides overflow,
     * and that the image is positioned relatively and has no max-width.
     *
     * @param  {object} crop            an object with the following properties:
     *                                  - selection: the crop selection (x, y, x2, y2)
     *                                  - width: the image width at time of cropping (can be less
     *                                    than the original)
     *                                  - height: the image height at time of cropping (can be less
     *                                    than the original)
     * @param  {jquery} $image          the image element to be cropped
     * @param  {jquery} $container      the container of the image
     * @param  {Number} column_width    the width of the containing element
     */
    ImageCropper.cropImage = function(crop, $image, $container, column_width) {
        // Remove any previous cropping
        $image.removeAttr('style');
        $container.removeAttr('style');

        // Math magics
        var selection_width = crop.selection.x2 - crop.selection.x;
        var selection_height = crop.selection.y2 - crop.selection.y;
        var scaled_width = crop.width / selection_width;
        var scaled_height = scaled_width; // Autoscale height to the new custom ratio

        // If the image is smaller than the column, Jcrop will not scale it to 100%, so factor in the difference
        var image_to_column_ratio = column_width / crop.width;
        scaled_width *= image_to_column_ratio;
        scaled_height *= image_to_column_ratio;

        var offset_left = crop.selection.x * scaled_width;
        var offset_top = crop.selection.y * scaled_height;

        // Now set the calculated values on the new content
        $image.css('width', crop.width * scaled_width + 'px');
        $image.css('height', crop.height * scaled_height + 'px');
        $image.css('margin-left', '-' + offset_left + 'px');
        $image.css('margin-top', '-' + offset_top + 'px');
        $container.css('height', selection_height * scaled_height + 'px');

        // Add class `cropped`
        $image.addClass('cropped');
    };

}(window.ImageCropper = window.ImageCropper || {}, jQuery ));
