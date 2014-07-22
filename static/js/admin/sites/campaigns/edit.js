$(function() {

    var wrapper = $('div.edit-campaign');
    var section_progress = wrapper.find('.section-progress');

    var button_introjs = wrapper.find('button[data-trigger="introjs"]');

    var save_form = section_progress.find('form.save');
    var existing_campaign = save_form.find('input[name="existing_campaign"]');
    var photographer_input = save_form.find('input[name="photographer"]');

    var campaign_container = wrapper.find('div.campaign-container');

    var user_image = wrapper.find('img.chosen-image');
    var user_image_ajaxloader = wrapper.find('img.chosen-image-ajaxloader');
    var user_image_cropped = campaign_container.find('img.cropped-image');

    var user_text_editors = wrapper.find('div.text-editors');
    var user_text_editor_template = wrapper.find('div.text-editor-template');
    var user_text_template = wrapper.find('div.text-template');

    var campaign_title = wrapper.find('input[name="campaign-title"]');

    var user_button_editor = wrapper.find('[data-container="edit-button"]');
    var user_button_exclude = user_button_editor.find('input[name="exclude-button"]');
    var user_button_anchor_input = user_button_editor.find('input[name="button-anchor"]');
    var user_button_large_input = user_button_editor.find('input[name="large-button"]');

    var user_button = campaign_container.find('.button');
    var user_button_anchor = user_button.find('a');

    var user_photographer = wrapper.find('.photographer');
    var user_photographer_name = user_photographer.find('span.name');
    var user_photographer_editor = wrapper.find('[data-edit="photographer"]');

    var JcropApi;
    var crop_ratio = [940, 480];
    var text_editor_id = 0; // Will be incremented for each created text editor (see below)

    button_introjs.click(function() {
        introJs.start();
    });

    // Load existing campaign data, if there
    if(existing_campaign.attr('data-campaign') !== '') {
        var campaign = JSON.parse(existing_campaign.attr('data-campaign'));

        setOriginalImage(campaign.image_original, [
            campaign.image_crop.selection.x,
            campaign.image_crop.selection.y,
            campaign.image_crop.selection.x2,
            campaign.image_crop.selection.y2,
        ], function() {
            user_image.data('crop.selection', campaign.image_crop.selection);
            user_image.data('crop.width', campaign.image_crop.width);
            user_image.data('crop.height', campaign.image_crop.height);

            // Add text
            for(var i=0; i<campaign.text.length; i++) {
                addText(campaign.text[i]);
            }

            // Reset button state

            // - Reset the editor
            user_button_exclude.prop('checked', !campaign.button_enabled);
            user_button_large_input.prop('checked', campaign.button_large);
            user_button_anchor_input.val(campaign.button_anchor);

            // - Disable editor controls if already disabled
            user_button_anchor_input.prop('disabled', !campaign.button_enabled);
            user_button_large_input.prop('disabled', !campaign.button_enabled);

            // - Set the styling on the actual buttno
            if(!campaign.button_enabled) {
                user_button.hide();
            }
            user_button.css('top', campaign.button_position.top);
            user_button.css('left', campaign.button_position.left);
            user_button_anchor.text(campaign.button_label);
            if(campaign.button_large) {
                user_button_anchor.addClass('btn-lg');
            }

            // Set the photographer state
            setPhotographer(
                campaign.photographer,
                campaign.photographer_alignment,
                campaign.photographer_color
            );

            // And default to the final step
            enableStep(3);
        });
    }

    section_progress.find('a').click(function() {
        if(Number($(this).attr('data-step')) > 1 && user_image.attr('src') === '') {
            alert(section_progress.attr('data-choose-image-warning'));
            return $(this);
        }
        enableStep(Number($(this).attr('data-step')));
    });

    save_form.submit(function(e) {
        if(user_image.attr('src') === '') {
            alert(section_progress.attr('data-choose-image-warning'));
            e.preventDefault();
            return $(this);
        }
    });

    wrapper.find('button.pick-from-image-archive').click(function() {
        ImageArchivePicker.pick(function(url, description, photographer) {
            setOriginalImage(url);
            setPhotographer(photographer.trim(), 'left', 'black'); // Default alignment/color
            enableStep(2);
        });
    });

    wrapper.find('button.upload-new-image').click(function() {
        ImageUploadDialog.open(function(url, description, photographer) {
            setOriginalImage(url);
            setPhotographer(photographer.trim(), 'left', 'black'); // Default alignment/color
            enableStep(2);
        });
    });

    wrapper.find('button.accept-crop').click(function() {
        enableStep(3, true); // Check the scale since this was an explicit crop
    });

    wrapper.find('button.add-text-editor').click(function() {
        addText();
    });

    /**
     * Change the original image and make it ready for cropping.
     * @param {string} image_url            the URL to the chosen image
     * @param {list}   predefined_selection an optional predefined crop-selection for this image
     */
    function setOriginalImage(image_url, predefined_selection, imageLoadedCallback) {
        if(JcropApi !== undefined) {
            JcropApi.destroy();
        }
        user_image.css('width', 'auto');
        user_image.css('height', 'auto');
        user_image.off('load.image');
        user_image.on('load.image', function() {
            // The image needs to be visible in the DOM for jcrop to base its wrapper on the correct image dimensions,
            // so display the step2 wrapper (which might be hidden) in the DOM (but hide its visibility) for the
            // duration of this function
            var step2 = wrapper.find('.step[data-step="2"]');
            var display = step2.css('display');
            step2.css('display', 'block');

            user_image_ajaxloader.hide();
            user_image.show();

            var setSelect;
            if(predefined_selection !== undefined) {
                setSelect = predefined_selection;
            } else {
                var image_ratio = user_image.width() / user_image.height();

                // Set the default selection as large as possible, but within the crop ratio
                var x2, y2;
                if(image_ratio > crop_ratio) {
                    x2 = user_image.width();
                    y2 = (user_image.width() / crop_ratio[0]) * crop_ratio[1];
                } else {
                    x2 = (user_image.height() / crop_ratio[1]) * crop_ratio[0];
                    y2 = user_image.height();
                }
                setSelect = [0, 0, x2, y2];
            }

            user_image.Jcrop({
                aspectRatio: crop_ratio[0] / crop_ratio[1],
                setSelect: setSelect,
                onSelect: function(selection) {
                    user_image.data('crop.selection', selection);
                },
            }, function() {
                JcropApi = this;

                // This will be overriden when going to step 3, but it should be set here as well in case
                // the user saves the campaign without going to step 3 at all
                user_image.data('crop.width', JcropApi.getBounds()[0]);
                user_image.data('crop.height', JcropApi.getBounds()[1]);
            });

            // And reset the wrapper display to whatever it was before
            step2.css('display', display);

            if(imageLoadedCallback !== undefined) {
                imageLoadedCallback();
            }
        });
        user_image.hide();
        user_image_ajaxloader.show();

        // Empty the src first to guarantee that the load.image event is thrown
        user_image.attr('src', '');
        user_image.attr('src', image_url);
    }

    function addText(options) {
        var id = text_editor_id++;

        options = $.extend({
            content: 'Tittel ' + (id+1),
            style: {
                top: '35px',
                left: '720px',
                'font-size': '48px',
                'font-weight': 'normal',
                color: '#000000',
            },
        }, options);

        // Clone and insert the text editor
        var text_editor = user_text_editor_template.clone();
        text_editor.removeClass('text-editor-template').addClass('text-editor').show();
        text_editor.attr('data-id', id);

        // Reset states based on options
        text_editor.find('p[data-trigger="content"]').text(options.content);
        text_editor.find('option[value="' + options.style['font-size'] + '"]').prop('selected', true);
        var bold = options.style['font-weight'] === 'bold';
        text_editor.find('input[name="bold"]').prop('checked', bold);
        text_editor.find('.colorselector div').css('background-color', options.style.color);

        // We need to append it to DOM before we initialize the color selector and chosen-select
        text_editor.appendTo(user_text_editors);

        var colorpicker = text_editor.find('.colorselector');
        colorpicker.ColorPicker({
            color: options.style.color,
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
                var id = colorpicker.parents('.text-editor').attr('data-id');
                campaign_container.find('.text[data-id="' + id + '"]').css('color', '#' + hex);
            }
        });
        text_editor.find('select').chosen();

        // Clone and insert the actual text
        var text = user_text_template.clone();
        text.removeClass('text-template').addClass('text').show();
        text.attr('data-id', id);
        text.html(options.content);
        text.css('top', options.style.top);
        text.css('left', options.style.left);
        text.css('font-size', options.style['font-size']);
        text.css('font-weight', options.style['font-weight']);
        text.css('color', options.style.color);
        text.appendTo(campaign_container);

        // Add events on text editor changes
        text_editor.find('select').change(function() {
            text.css('font-size', $(this).find('option:selected').val());
        });

        text_editor.find('input[name="bold"]').change(function() {
            if($(this).is(':checked')) {
                text.css('font-weight', 'bold');
            } else {
                text.css('font-weight', 'normal');
            }
        });

        // Add events on text-change to update text-editor content
        text.keyup(function() {
            text_editor.find('p[data-trigger="content"]').text($(this).text());
        });
    }

    $(document).on('click', '.text-editor a[data-trigger="remove"]', function() {
        var text_editor = $(this).parents('.text-editor');
        var id = text_editor.attr('data-id');
        text_editor.remove();
        campaign_container.find('.text[data-id="' + id + '"]').remove();
    });

    user_button_exclude.change(function() {
        var checked = $(this).is(':checked');
        user_button_anchor_input.prop('disabled', checked);
        user_button_large_input.prop('disabled', checked);

        if(checked) {
            user_button.hide();
        } else {
            user_button.show();
        }
    });

    user_button_large_input.change(function() {
        if($(this).is(':checked')) {
            user_button_anchor.addClass('btn-lg');
        } else {
            user_button_anchor.removeClass('btn-lg');
        }
    });

    user_button_anchor_input.keyup(function() {
        user_button_anchor.attr('href', $(this).val());
    });

    user_button_anchor.click(function(e) {
        e.preventDefault();
    });

    user_photographer_editor.find('input[name="photographer-alignment"]').change(function() {
        if($(this).val() === 'left') {
            user_photographer.css('left', '5px');
            user_photographer.css('right', 'auto');
        }  else {
            user_photographer.css('left', 'auto');
            user_photographer.css('right', '5px');
        }
    });

    user_photographer_editor.find('input[name="photographer-color"]').change(function() {
        user_photographer.css('color', $(this).val());
    });

    save_form.submit(function() {
        var form_data = {
            title: campaign_title.val(),
            image_original: user_image.attr('src'),
            image_crop: {
                selection: user_image.data('crop.selection'),
                width: user_image.data('crop.width'),
                height: user_image.data('crop.height'),
            },
            photographer_alignment: user_photographer_editor.find('input[name="photographer-alignment"]:checked').val(),
            photographer_color: user_photographer_editor.find('input[name="photographer-color"]:checked').val(),
            button_enabled: !user_button_exclude.is(':checked'),
            button_label: user_button_anchor.html(),
            button_anchor: user_button_anchor_input.val(),
            button_large: user_button_large_input.is(':checked'),
            button_position: {
                top: user_button.css('top'),
                left: user_button.css('left'),
            },
            text: [],
        };

        campaign_container.find('.text').each(function() {
            form_data.text.push({
                content: $(this).html(),
                style: {
                    'top': $(this).css('top'),
                    'left': $(this).css('left'),
                    'font-size': $(this).css('font-size'),
                    'font-weight': $(this).css('font-weight'),
                    'color': $(this).css('color'),
                },
            });
        });

        save_form.find('input[name="campaign"]').val(JSON.stringify(form_data));
    });

    /**
     * Dragging text elements
     */
    var dragged_text;

    $(document.body).on('mousemove', '.campaign-container', function(e) {
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
            if(top > campaign_container.height() - dragged_text.height()) {
                dragged_text.css('top', campaign_container.height() - dragged_text.height() + 'px');
            }
            if(left > campaign_container.width() - dragged_text.width()) {
                dragged_text.css('left', campaign_container.width() - dragged_text.width() + 'px');
            }
        }
    });

    $(document.body).on('mousedown', '.campaign-container .movable', function(e) {
        if($(e.target).is('.movable')) {
            dragged_text = $(e.target);
        } else {
            dragged_text = $(e.target).parents('.movable');
        }
    });

    $(document.body).on('mouseup', function(e) {
        dragged_text = undefined;
    });

    $(document.body).on('dragover drop', '.campaign-container', function(e) {
        e.preventDefault();
    });

    function setPhotographer(photographer, alignment, color) {
        photographer_input.val(photographer);
        if(photographer === '') {
            user_photographer.hide();
            user_photographer_editor.hide();
        } else {
            user_photographer.show();
            user_photographer_name.text(photographer);
            user_photographer_editor.show();
            var alignment_input = user_photographer_editor.find('input[name="photographer-alignment"][value="' + alignment + '"]');
            var color_input = user_photographer_editor.find('input[name="photographer-color"][value="' + color + '"]');
            alignment_input.prop('checked', true);
            alignment_input.parent().addClass('active');
            color_input.prop('checked', true);
            color_input.parent().addClass('active');

            // Update actual state
            if(alignment === 'left') {
                user_photographer.css('left', '5px');
                user_photographer.css('right', 'auto');
            }  else {
                user_photographer.css('left', 'auto');
                user_photographer.css('right', '5px');
            }
            user_photographer.css('color', color);

        }
    }

    $(document.body).on('keypress', '.campaign-container .movable', function(e) {
        // Largest character is about this size
        var minimum_buffer = 60;

        var left = $(this).css('left');
        left = Number(left.substring(0, left.length - 2));
        var right_offset = left + $(this).width();

        if(campaign_container.width() - right_offset <= minimum_buffer) {
            if(left <= minimum_buffer) {
                alert(campaign_container.attr('data-too-long-sentence-warning'));
                e.preventDefault();
            } else {
                $(this).css('left', (left - minimum_buffer) + 'px');
            }
        }
    });

    function enableStep(step, checkScale) {
        section_progress.find('li').removeClass('active');
        section_progress.find('li').eq(step - 1).addClass('active');
        wrapper.find('div.step').hide();
        wrapper.find('div.step[data-step="' + step + '"]').show();

        if(step === 3) {
            user_image_cropped.attr('src', user_image.attr('src'));

            // Set the dimensions used for scaling at this point because we need to get it from the Jcrop API
            // bounds. Calling width() on the jquery element may give wrong results here.
            user_image.data('crop.width', JcropApi.getBounds()[0]);
            user_image.data('crop.height', JcropApi.getBounds()[1]);

            ImageCropper.cropImage({
                    selection: user_image.data('crop.selection'),
                    width: user_image.data('crop.width'),
                    height: user_image.data('crop.selection'),
                },
                user_image_cropped,
                campaign_container,
                crop_ratio[0]
            );

            // checkScale is true when we're explicitly cropping and want to warn the user when applicable
            if(checkScale && user_image.get(0).naturalWidth !== undefined && user_image_cropped.width() > user_image.get(0).naturalWidth) {
                if(!confirm(user_image.attr('data-image-scale-warning'))) {
                    enableStep(2);
                    return;
                }
            }

            // Add an initial text editor if it's empty
            if(user_text_editors.children().length === 0) {
                addText();
            }
        }
    }

});
