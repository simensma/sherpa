$(function() {

    var wrapper = $('div.new-campaign');
    var section_progress = wrapper.find('.section-progress');
    var save_form = section_progress.find('form.save');
    var chosen_image = wrapper.find('img.chosen-image');
    var chosen_image_ajaxloader = wrapper.find('img.chosen-image-ajaxloader');
    var cropped_image_container = wrapper.find('div.cropped-image-container');
    var cropped_image = cropped_image_container.find('img.cropped-image');
    var text_areas = wrapper.find('div.text-areas');
    var text_area_template = wrapper.find('div.text-area-template');
    var text_template = wrapper.find('div.text-template');

    var button_wrapper = wrapper.find('[data-wrapper="campaign-button"]');
    var exclude_button = button_wrapper.find('input[name="exclude-button"]');
    var button_anchor = button_wrapper.find('input[name="button-anchor"]');
    var large_button = button_wrapper.find('input[name="large-button"]');
    var custom_button = cropped_image_container.find('.button');

    var JcropApi;
    var crop_ratio = [940, 480];
    var text_area_id = 0; // Will be incremented for each created text area (see below)

    section_progress.find('a').click(function() {
        if(Number($(this).attr('data-step')) > 1 && chosen_image.attr('src') === '') {
            alert(section_progress.attr('data-choose-image-warning'));
            return $(this);
        }
        enableStep(Number($(this).attr('data-step')));
    });

    save_form.submit(function(e) {
        if(chosen_image.attr('src') === '') {
            alert(section_progress.attr('data-choose-image-warning'));
            e.preventDefault();
            return $(this);
        }
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

    wrapper.find('button.add-text-area').click(function() {
        addText();
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
        ImageCropper.cropImage(
            chosen_image.data('crop'),
            cropped_image,
            cropped_image_container,
            crop_ratio[0]
        );
    }

    function addText() {
        var id = text_area_id++;

        // Clone and insert the text area
        var text_area = text_area_template.clone();
        text_area.removeClass('text-area-template').addClass('text-area').show();
        text_area.attr('data-id', id);
        text_area.appendTo(text_areas);
        var colorpicker = text_area.find('.colorselector');
        colorpicker.ColorPicker({
            color: '#000000',
            onShow: function(picker) {
                $(picker).fadeIn('fast');
                return false;
            },
            onHide: function(picker) {
                $(picker).fadeOut('fast');
                return false;
            },
            onChange: function (hsb, hex, rgb) {
                colorpicker.children('div').css('background-color', '#' + hex);
                var id = colorpicker.parents('.text-area').attr('data-id');
                cropped_image_container.find('.text[data-id="' + id + '"]').css('color', '#' + hex);
            }
        });
        text_area.find('select').chosen();

        // Clone and insert the actual text
        var text = text_template.clone();
        text.removeClass('text-template').addClass('text').show();
        text.attr('data-id', id);
        text.text(text.text() + ' ' + (id+1));
        text.css('font-size', text_area.find('select option:selected').val());
        text.css('top', 0);
        text.css('left', 0);
        text.appendTo(cropped_image_container);

        // Add events on text area changes
        text_area.find('select').change(function() {
            text.css('font-size', $(this).find('option:selected').val());
        });

        text_area.find('input[name="bold"]').change(function() {
            if($(this).is(':checked')) {
                text.css('font-weight', 'bold');
            } else {
                text.css('font-weight', 'normal');
            }
        });
    }

    $(document).on('click', '.text-area button.remove', function() {
        var text_area = $(this).parents('.text-area');
        var id = text_area.attr('data-id');
        text_area.remove();
        cropped_image_container.find('.text[data-id="' + id + '"]').remove();
    });

    exclude_button.change(function() {
        var checked = $(this).is(':checked');
        button_anchor.prop('disabled', checked);
        large_button.prop('disabled', checked);

        if(checked) {
            custom_button.hide();
        } else {
            custom_button.show();
        }
    });

    large_button.change(function() {
        if($(this).is(':checked')) {
            custom_button.find('a').addClass('btn-lg');
        } else {
            custom_button.find('a').removeClass('btn-lg');
        }
    });

    button_anchor.keyup(function() {
        custom_button.find('a').attr('href', $(this).val());
    });

    custom_button.find('a').click(function(e) {
        e.preventDefault();
    });

    /**
     * Dragging text elements
     */
    var dragged_text;

    $(document.body).on('mousemove', '.cropped-image-container', function(e) {
        e.preventDefault();
        if(dragged_text !== undefined) {
            dragged_text.offset({
                top: e.pageY,
                left: e.pageX
            });

            // Check boundaries (keep the text inside the container)
            var top_css = dragged_text.css('top');
            var top = Number(top_css.substring(0, top_css.length - 2));
            var left_css = dragged_text.css('left');
            var left = Number(left_css.substring(0, left_css.length - 2));

            if(top < 0) {
                dragged_text.css('top', '0px');
            }
            if(left < 0) {
                dragged_text.css('left', '0px');
            }
            if(top > cropped_image_container.height() - dragged_text.height()) {
                dragged_text.css('top', cropped_image_container.height() - dragged_text.height() + 'px');
            }
            if(left > cropped_image_container.width() - dragged_text.width()) {
                dragged_text.css('left', cropped_image_container.width() - dragged_text.width() + 'px');
            }
        }
    });

    $(document.body).on('mousedown', '.cropped-image-container .campaign-element', function(e) {
        if($(e.target).is('.campaign-element')) {
            dragged_text = $(e.target);
        } else {
            dragged_text = $(e.target).parents('.campaign-element');
        }
    });

    $(document.body).on('mouseup', function(e) {
        dragged_text = undefined;
    });

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
