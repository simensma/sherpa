$(function() {

    var wrapper = $('div.edit-campaign');
    var section_progress = wrapper.find('.section-progress');

    var save_form = section_progress.find('form.save');
    var existing_campaign = save_form.find('input[name="existing_campaign"]');

    var campaign_container = wrapper.find('div.campaign-container');

    var user_image = wrapper.find('img.chosen-image');
    var user_image_ajaxloader = wrapper.find('img.chosen-image-ajaxloader');
    var user_image_cropped = campaign_container.find('img.cropped-image');

    var user_text_editors = wrapper.find('div.text-editors');
    var user_text_editor_template = wrapper.find('div.text-editor-template');
    var user_text_template = wrapper.find('div.text-template');

    var campaign_title = wrapper.find('input[name="campaign-title"]');

    var user_button_editor = wrapper.find('[data-wrapper="campaign-button"]');
    var user_button_exclude = user_button_editor.find('input[name="exclude-button"]');
    var user_button_anchor_input = user_button_editor.find('input[name="button-anchor"]');
    var user_button_large_input = user_button_editor.find('input[name="large-button"]');

    var user_button = campaign_container.find('.button');
    var user_button_anchor = user_button.find('a');

    var JcropApi;
    var crop_ratio = [940, 480];
    var text_editor_id = 0; // Will be incremented for each created text editor (see below)

    // Load existing campaign data, if there
    if(existing_campaign.attr('data-campaign') !== '') {
        var campaign = JSON.parse(existing_campaign.attr('data-campaign'));

        showImage(campaign.image_url, [
            campaign.image_crop.selection.x,
            campaign.image_crop.selection.y,
            campaign.image_crop.selection.x2,
            campaign.image_crop.selection.y2,
        ]);
        user_image.data('crop', campaign.image_crop);

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

        // And default to the final step
        enableStep(3);
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

    wrapper.find('button.add-text-editor').click(function() {
        addText();
    });

    function showImage(image_url, predefined_selection) {
        if(JcropApi !== undefined) {
            JcropApi.destroy();
        }
        user_image.css('width', 'auto');
        user_image.css('height', 'auto');
        user_image.off('load.image');
        user_image.on('load.image', function() {
            user_image_ajaxloader.hide();
            user_image.show();

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

            user_image.Jcrop({
                aspectRatio: crop_ratio[0] / crop_ratio[1],
                setSelect: [0, 0, x2, y2],
                onSelect: function(selection) {
                    user_image.data('crop', {
                        selection: selection,
                        width: user_image.width(),
                        height: user_image.height(),
                    });
                },
            }, function() {
                JcropApi = this;
            });

            if(predefined_selection !== undefined) {
                JcropApi.setSelect(predefined_selection);
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
                top: '0',
                left: '0',
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
    }

    $(document).on('click', '.text-editor button.remove', function() {
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

    save_form.submit(function() {
        var form_data = {
            title: campaign_title.val(),
            image_url: user_image.attr('src'),
            image_crop: user_image.data('crop'),
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

    $(document.body).on('mousedown', '.campaign-container .campaign-element', function(e) {
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
            user_image_cropped.attr('src', user_image.attr('src'));
            ImageCropper.cropImage(
                user_image.data('crop'),
                user_image_cropped,
                campaign_container,
                crop_ratio[0]
            );

            // Add an initial text editor if it's empty
            if(user_text_editors.children().length === 0) {
                addText();
            }
        }
    }

});
