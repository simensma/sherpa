$(function() {

    var wrapper = $('div.new-campaign');
    var section_progress = wrapper.find('.section-progress');
    var chosen_image = wrapper.find('img.chosen-image');
    var chosen_image_ajaxloader = wrapper.find('img.chosen-image-ajaxloader');
    var cropped_image_container = wrapper.find('div.cropped-image-container');
    var cropped_image = cropped_image_container.find('img.cropped-image');
    var text_areas = wrapper.find('div.text-areas');
    var text_area_template = wrapper.find('div.text-area-template');

    var JcropApi;
    var crop_ratio = [940, 480];

    section_progress.find('a').click(function() {
        if(Number($(this).attr('data-step')) > 1 && chosen_image.attr('src') === '') {
            alert(section_progress.attr('data-choose-image-warning'));
            return $(this);
        }
        enableStep(Number($(this).attr('data-step')));
    });

    wrapper.find('button.pick-from-image-archive').click(function() {
        ImageArchivePicker.pick(function(url, description, photographer) {
            showImage(url);
            enableStep(2);
        });
    });

    wrapper.find('button.upload-new-image').click(function() {
        ImageUploadDialog.open(function(url, description, photographer) {
            showImage(url);
            enableStep(2);
        });
    });

    wrapper.find('button.accept-crop').click(function() {
        enableStep(3);
    });

    function showImage(image_url) {
        if(JcropApi !== undefined) {
            JcropApi.destroy();
        }
        chosen_image.css('width', 'auto');
        chosen_image.css('height', 'auto');
        chosen_image.off('load.image');
        chosen_image.on('load.image', function() {
            chosen_image_ajaxloader.hide();
            chosen_image.show();

            var image_ratio = chosen_image.width() / chosen_image.height();

            // Set the default selection as large as possible, but within the crop ratio
            var x2, y2;
            if(image_ratio > crop_ratio) {
                x2 = chosen_image.width();
                y2 = (chosen_image.width() / crop_ratio[0]) * crop_ratio[1];
            } else {
                x2 = (chosen_image.height() / crop_ratio[1]) * crop_ratio[0];
                y2 = chosen_image.height();
            }

            chosen_image.Jcrop({
                aspectRatio: crop_ratio[0] / crop_ratio[1],
                setSelect: [0, 0, x2, y2],
                onSelect: function(selection) {
                    chosen_image.data('crop', {
                        selection: selection,
                        width: chosen_image.width(),
                        height: chosen_image.height(),
                    });
                },
            }, function() {
                JcropApi = this;
            });

        });
        chosen_image.hide();
        chosen_image_ajaxloader.show();
        chosen_image.attr('src', image_url);
    }

    function cropImage() {
        cropped_image.attr('src', chosen_image.attr('src'));

        var crop = chosen_image.data('crop');

        // Remove any previous cropping
        cropped_image.removeAttr('style');
        cropped_image_container.removeAttr('style');

        // Math magics
        var column_width = crop_ratio[0];
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
        cropped_image.css('width', crop.width * scaled_width + 'px');
        cropped_image.css('height', crop.height * scaled_height + 'px');
        cropped_image.css('margin-left', '-' + offset_left + 'px');
        cropped_image.css('margin-top', '-' + offset_top + 'px');
        cropped_image_container.css('height', selection_height * scaled_height + 'px');
    }

    function addText() {
        var text_area = text_area_template.clone();
        text_area.removeClass('text-area-template').addClass('text-area').show();
        text_area.appendTo(text_areas);
        text_area.find('select').chosen();
    }

    function enableStep(step) {
        section_progress.find('li').removeClass('active');
        section_progress.find('li').eq(step - 1).addClass('active');
        wrapper.find('div.step').hide();
        wrapper.find('div.step[data-step="' + step + '"]').show();

        if(step === 3) {
            cropImage();

            // Add an initial text area if it's empty
            if(text_areas.children().length === 0) {
                addText();
            }
        }
    }

});
