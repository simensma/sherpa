$(function() {

    $("div.content.image[data-crop]").each(function() {
        var crop = JSON.parse($(this).attr('data-crop'));
        var image = $(this).find("img");

        // Remove any previous cropping
        image.removeAttr('style');
        $(this).removeAttr('style');

        // Math magics
        var column_width = $(this).parent().width();
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
        image.css('width', crop.width * scaled_width + 'px');
        image.css('height', crop.height * scaled_height + 'px');
        image.css('margin-left', '-' + offset_left + 'px');
        image.css('margin-top', '-' + offset_top + 'px');
        $(this).css('height', selection_height * scaled_height + 'px');

    });

});
