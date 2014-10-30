/* CMS Editor: Content-editing (HTML, images, widgets) */

$(function() {

    var editor = $("div.cms-editor");
    var article = editor.find("article");
    var insertion_templates = editor.find('[data-dnt-container="insertion-templates"]');
    var editor_header =$('.editor-header');
    var toolbars_container = $('.sticky [data-dnt-container="toolbars"]');

    disableIframes(article.find('[data-dnt-container="content-widget"]'));

    // Crop cropped images on page load
    article.find("div.content.image").each(function() {
        if(JSON.parse($(this).attr('data-json')).crop !== undefined) {
            cropContent($(this));
        }
    });

    // Highlight contenteditables that are being edited
    $(document).on('focus', 'article div.editable', function() {
        $(this).addClass('selected');
    });
    $(document).on('focusout', 'article div.editable', function() {
        $(this).removeClass('selected');
    });

    // Highlight empty html contents
    $(document).on('click', 'article div.content.html[data-placeholder], article div.content.lede[data-placeholder]', function() {
        $(this).removeAttr('data-placeholder');
        $(this).text('');
        $(this).attr('contenteditable', 'true');
        $(this).focus();
    });

    $(document).on('focusout', 'article div.content.html, article div.content.lede', function() {
        if($(this).text().trim() === "" && $(this).children("hr").length === 0) {
            $(this).removeAttr('contenteditable');
            $(this).attr('data-placeholder', '');
            if($(this).hasClass('html')) {
                $(this).text("Klikk for å legge til tekst...");
            } else if($(this).hasClass('lede')) {
                $(this).text("Klikk for å legge til ingress...");
            }
        }
    });

    // Change image sources upon being clicked
    $(document).on('click', 'article div.content.image', function() {
        var content = $(this);
        var json_content = JSON.parse(content.attr('data-json'));
        if(json_content.anchor === null) {
            json_content.anchor = '';
        }

        ImageDialog.open({
            src: json_content.src,
            anchor: json_content.anchor,
            description: json_content.description,
            photographer: json_content.photographer,
            save: function(src, anchor, description, photographer) {
                var image_content = insertion_templates.find("div.content.image").clone();
                content.replaceWith(image_content);
                if(anchor === '') {
                    // No anchor, remove the anchor element
                    anchor = null;
                    image_content.find("a").replaceWith(image_content.find("a img"));
                } else {
                    image_content.find("a").attr('href', anchor);
                }
                image_content.find("img").attr('src', src);
                image_content.find("img").attr('alt', description);
                image_content.find("span.description-content").text(description);
                image_content.find("span.photographer span.content").text(photographer);

                if(description === '' && photographer === '') {
                    image_content.find("div.description").remove();
                } else if(description === '') {
                    image_content.find("div.description span.description").remove();
                } else if(photographer === '') {
                    image_content.find("div.description span.photographer").remove();
                }

                image_content.attr('data-json', JSON.stringify({
                    src: src,
                    anchor: anchor,
                    description: description,
                    photographer: photographer,
                    crop: json_content.crop,
                }));
            },
        });
    });

    // Edit an existing widget
    $(document).on('click', article.selector + ' [data-dnt-container="content-widget"]', function() {
        var widget_element = $(this);
        var widget_content = JSON.parse($(this).attr('data-json'));
        $(this).trigger('widget.edit', [widget_content, function(widget) {
            var prev = widget_element.prevAll("div.content").first();
            var column = widget_element.parents("div.column");
            widget_element.remove();

            var position;
            if(prev.length === 0) {
                position = {insertion: 'prepend', existingElement: column};
            } else {
                position = {insertion: 'after', existingElement: prev};
            }

            Editor.insertContent({type: 'widget', widget: widget}, position);
        }]);
    });

    // Show content control icons upon hovering content
    $(document).on('mouseenter', 'article div.content', function() {
        if(EditorMoveContent.isMoving()) {
            // Ignore this while moving
            return $(this);
        }
        if($(this).prevAll("div.content-control").length >= 1) {
            // Ignore if they're already there (happens when mouse goes from content directly to control and back)
            return $(this);
        }
        if($(this).is(".image")) {
            // Insert the cropper only for images
            insertion_templates.find("div.crop-content").clone().insertBefore($(this)).tooltip();
        }
        insertion_templates.find("div.remove-content").clone().insertBefore($(this)).tooltip();
        insertion_templates.find("div.move-content").clone().insertBefore($(this)).tooltip();
    });

    // Add CSS class hover to the content belonging to content control on mouseover
    $(document).on('mouseover', 'div.content-control', function (e) {
        var $content = $(this).nextAll('div.content').first();
        $content.addClass('hover');
    });

    // Remove CSS class hover to the content belonging to content control on mouseout
    $(document).on('mouseout', 'div.content-control', function (e) {
        var $content = $(this).nextAll('div.content').first();
        $content.removeClass('hover');
    });

    // Remove the content control icons upon mouse leave
    $(document).on('mouseleave', 'article div.content', function(e) {
        if(EditorMoveContent.isMoving()) {
            // Ignore this while moving
            return $(this);
        }

        if(contains($(this), e.pageX, e.pageY)) {
            // Mouse is still inside the content, presumably hovering content-controls; don't remove them
        } else {
            $(this).siblings("div.content-control").remove();
        }
    });

    // Also remove them when mouse leaves the icons themselves
    $(document).on('mouseleave', 'article div.content-control', function(e) {
        if(contains($(this).nextAll("div.content").first(), e.pageX, e.pageY)) {
            // Mouse is still inside the content, presumably hovering content-controls; don't remove them
        } else {
            $(this).siblings("div.content-control").remove();
            $(this).remove();
        }
    });

    // Confirm and remove content when 'remove-content' icon clicked
    $(document).on('click', 'article div.remove-content', function(e) {
        e.stopPropagation(); // Avoid click-event on an image or widget
        // Some browsers may handle mouse movement events even after confirm-window is opened, and that
        // may detach the content-control. So save the content-reference before continuing
        var content = $(this).nextAll("div.content").first();
        if(confirm($(this).attr('data-confirm'))) {
            content.slideUp(function() {
                $(this).remove();
                Editor.resetControls();
            });
            $(this).tooltip('destroy');
            $(this).siblings("div.content-control").remove();
            $(this).remove();
        }
    });

    // Enable content moving on 'move-content' icon click
    $(document).on('click', 'article div.move-content', function(e) {
        e.stopPropagation(); // Avoid click-event on an image or widget
        EditorMoveContent.init({
            content: $(this).nextAll("div.content").first(),
            endCallback: Editor.resetControls,
        });
        $(this).tooltip('destroy'); // Just in case the browser doesn't trigger the mouseleave
        $(this).siblings("div.content-control").remove();
        $(this).remove();
    });

    // Choose crop ratio on 'crop-content' icon click
    var JcropApi;
    $(document).on('click', 'article div.crop-content', function(e) {

        if (JcropApi) {
            toolbars_container.find('div.crop-control button.use').first().click();
        }

        e.stopPropagation(); // Avoid click-event on an image or widget
        var content = $(this).nextAll("div.content").first();
        var crop = JSON.parse(content.attr('data-json')).crop;

        // Remove the original cropping selection, if any. We want the image element to be full-size while
        // cropping, and we'll use a clone of this original non-cropped element when cancelling the clone.
        if(crop !== undefined) {
            var image = content.find("img");
            image.removeAttr('style');
            image.removeClass('cropped');
            content.removeAttr('style');
        }

        // Set up crop control elements
        var crop_control = insertion_templates.find("div.toolbar-crop-control").clone().addClass('jq-hide');
        toolbars_container.html(crop_control);

        var crop_control_height = crop_control.outerHeight();
        crop_control.css('margin-top', -crop_control_height);
        crop_control.removeClass('jq-hide');
        crop_control.animate(
            {
                'margin-top': 0
            },
            {
                duration: 250,
                complete: function() {
                    $(this).css('z-index', 0);
                }
            }
        );

        crop_control.data('original-content', content);
        crop_control.data('content-clone', content.clone().removeClass('hover'));
        if(crop === undefined) {
            // Hide the controls by default for the first selection; until cropping selection has been made
            crop_control.find("div.submit").css('display', 'none');
        }

        $(this).siblings("div.content-control").tooltip('destroy').remove();
        $(this).tooltip('destroy').remove();

        // Default to free
        crop_control.find("div.choose-ratio button[data-ratio='free']").click();
    });

    // Selecting a cropping ratio
    $(document).on('click', 'div.crop-control div.choose-ratio button', function() {
        var crop_control = $(this).parents("div.crop-control");
        var content = crop_control.data('original-content');
        var original_crop = JSON.parse(content.attr('data-json')).crop;
        var ratio = $(this).attr('data-ratio');
        var aspect_ratio;

        if (ratio !== 'free') {
            aspect_ratio = ratio.split(":")[0] / ratio.split(":")[1];
        } else {
            aspect_ratio = false;
        }

        // Highlight the marked button
        $(this).siblings().removeClass('btn-danger active');
        $(this).addClass('btn-danger');

        // Enable the actual cropping
        content.Jcrop({
            aspectRatio: aspect_ratio,
            onSelect: function(selection) {
                crop_control.find("div.submit").css('display', 'block');
                var image_json = JSON.parse(content.attr('data-json'));
                image_json.crop = {
                    selection: selection,
                    width: content.find("img").width(),
                    height: content.find("img").height(),
                };
                content.attr('data-json', JSON.stringify(image_json));
            },
        }, function() {
            JcropApi = this;
        });

        var x1, y1, x2, y2;
        var content_width = content.width();
        var content_height = content.height();

        // Reapply the original selection to the cropper ui, if any
        if (original_crop !== undefined) {

            // In case we're cropping in a different column size, factor in the difference
            var image_width_ratio = content_width / original_crop.width;
            var image_height_ratio = content_height / original_crop.height;

            x1 = original_crop.selection.x * image_width_ratio;
            y1 = original_crop.selection.y * image_height_ratio;
            x2 = original_crop.selection.x2 * image_width_ratio;
            y2 = original_crop.selection.y2 * image_height_ratio;

        } else {

            if (ratio === 'free') {
                x1 = 0;
                y1 = 0;
                x2 = content_width;
                y2 = content_height;
            }
        }

        if (typeof x1 === 'number' && typeof x2 === 'number' && typeof y1 === 'number' && typeof y2 === 'number') {
            // Why does it take an array here, while it gives us an object in the event!? Tsk
            JcropApi.setSelect([
                x1, y1, x2, y2
            ]);
        }

    });

    $(document).on('click', 'div.crop-control div.submit button.use', function(e) {
        var crop_control = $(this).parents("div.crop-control");
        var original_content = crop_control.data('original-content');
        var original_image = original_content.find("img");
        var jcrop_holder = original_content.parents('.jcrop-holder').first();
        var new_content = crop_control.data('content-clone');
        var new_image = new_content.find("img");
        var crop = JSON.parse(original_content.attr('data-json')).crop;

        if(crop === undefined) {
            $(this).siblings("button.remove").click();
            return $(this);
        }

        new_content.attr('data-json', original_content.attr('data-json'));
        new_content.insertAfter(jcrop_holder);
        cropContent(new_content);
        endCropping(crop_control);
    });

    // Remove crop, restore image to original
    $(document).on('click', 'div.crop-control div.submit button.remove', function(e) {
        var crop_control = $(this).parents("div.crop-control");
        var clone = crop_control.data('content-clone');
        var original_content = crop_control.data('original-content');
        var jcrop_holder = original_content.parents('.jcrop-holder').first();
        var json = JSON.parse(clone.attr('data-json'));
        json.crop = undefined;
        clone.attr('data-json', JSON.stringify(json)).insertAfter(jcrop_holder);
        endCropping(crop_control);
    });

    function endCropping(crop_control) {
        if (JcropApi !== undefined) {
            JcropApi.destroy();
            JcropApi = undefined;
        }
        crop_control.remove();
    }

    // Doesn't really need to be its own method as its semantics are:
    // 1. Crop the content with ImageCropper
    // 2. Add the 'cropped' class
    // but since we're performing this logic twice, why not.
    function cropContent(content) {
        ImageCropper.cropImage(
            JSON.parse(content.attr('data-json')).crop,
            content.find('img'),
            content,
            content.parents('div.column').width()
        );
        content.find('img').addClass('cropped');
    }

    // Global disable-iframes function
    window.disableIframes = disableIframes;
    function disableIframes(content) {
        // Can't capture click events in iframes, so replace them
        content.find("iframe").each(function() {
            var width = $(this).css('width');
            var height = $(this).css('height');
            var div = $('<div style="background: url(/static/img/admin/sites/editor/iframe-placeholder.png) top left repeat; max-width: 100%">&nbsp;</div>');
            div.css('width', width);
            div.css('height', height);
            $(this).replaceWith(div);
        });
    }

    // Returns true if the given element position contains the given mouse coordinates
    function contains(element, mouseX, mouseY) {
        var objX = element.offset().left;
        var objY = element.offset().top;
        var objW = element.width();
        var objH = element.height();
        return mouseX >= objX && mouseX <= objX + objW && mouseY >= objY && mouseY <= objY + objH;
    }

});
