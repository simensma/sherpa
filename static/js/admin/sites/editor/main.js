/* The main CMS editor functionality */

$(function() {

    var editor = $("div.cms-editor");
    var article = editor.find("article");
    var insertion_templates = editor.find("div.insertion-templates");
    var toolbar = editor.find("div.cms-editor-toolbar");
    var toolbarContents = toolbar.find("div.toolbar-contents");

    //
    // Initialization
    //

    rangy.init();
    window.selection = undefined;
    disableIframes(article.find("div.content.widget"));
    resetControls();

    // Crop cropped images on page load
    article.find("div.content.image").each(function() {
        if(JSON.parse($(this).attr('data-json')).crop !== undefined) {
            cropContent($(this));
        }
    });

    // Make toolbar draggable, but not if input-elements are clicked
    toolbar.draggable();
    toolbar.find("input,select,button,a").mousedown(function(e) {
        e.stopPropagation();
    });

    // Draggable will set position relative, so make sure it is fixed before the user drags it
    toolbar.css('position', 'fixed');

    // Prevent all anchor clicks within the article
    $(document).on('click', article.selector + ' a', function(e) {
        e.preventDefault();
    });

    // Highlight contenteditables that are being edited
    $(document).on('focus', 'article div.editable', function() {
        $(this).addClass('selected');
    });
    $(document).on('focusout', 'article div.editable', function() {
        $(this).removeClass('selected');
    });

    // Set the selection when appropriate
    $(document).on('mouseup', 'article div.editable', setSelection);
    $(document).on('keyup', 'article div.editable', setSelection);
    function setSelection() {
        selection = rangy.getSelection();
    }

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
                image_content.find("span.description").text(description);
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

    // Add content (expand plus-icon into available content items)
    $(document).on('click', article.selector + ' div.add-content,' + article.selector + ' div.add-content-row', function() {
        $(this).addClass('active');
        // The container may change size, so make sure the tooltip is removed
        // Simply hiding it was buggy, so try destroying and recreating it
        $(this).tooltip('destroy');
        $(this).tooltip({placement: 'bottom'});
        $(this).tooltip('show');
    });

    // Cancel add-content on mouse out
    $(document).on('mouseleave', article.selector + ' div.add-content,' + article.selector + ' div.add-content-row', function() {
        $(this).removeClass('active');
    });

    // Add chosen content-type
    $(document).on('click', article.selector + " div.add-content button", function() {
        // Manually hide the tooltips since mouseleave won't be triggered
        $(this).tooltip('hide');
        $(this).parents("div.add-content,div.add-content-row").tooltip('hide');

        var type = $(this).attr('data-type');
        var widget_type = $(this).attr('data-widget');
        var prev = $(this).parents("div.add-content").prevAll("div.content").first();
        var column = $(this).parents("div.column");

        var position;
        if(prev.length === 0) {
            position = {insertion: 'prepend', existingElement: column};
        } else {
            position = {insertion: 'after', existingElement: prev};
        }

        if(type !== 'widget') {
            insertContent({type: type}, position);
        } else {
            $(document).trigger('widget.new.' + widget_type, function(widget) {
                insertContent({type: type, widget: widget}, position);
            });
        }
    });

    // Add chosen content-type (separate logic for row-based addition)
    $(document).on('click', article.selector + ' div.add-content-row button', function() {
        // Trigger mouseout manually so that the tooltip is removed
        $(this).trigger('mouseout');

        var type = $(this).attr('data-type');
        var widget_type = $(this).attr('data-widget');
        var prev_row = $(this).parents("div.row-fluid").prev("div[data-row]");

        var position;
        if(prev_row.length > 0 && prev_row.children("div.column").length === 1) {
            // The previous row exists and is a single-column; just add an element to that row
            position = {insertion: 'append', existingElement: prev_row.children("div.column")};
        } else {
            // No previous row or not single-column; create a new row
            var new_row = insertion_templates.find('[data-row]').clone();
            new_row.insertAfter($(this).parents("div.row-fluid"));
            position = {insertion: 'prepend', existingElement: new_row.find("div.column")};
        }

        if(type !== 'widget') {
            insertContent({type: type}, position);
        } else {
            $(document).trigger('widget.new.' + widget_type, function(widget) {
                insertContent({type: type, widget: widget}, position);
            });
        }
    });

    // Insert the specified content at the specified position
    function insertContent(content, position) {
        function insertItem(item, position) {
            if(position.insertion === 'after') {
                item.insertAfter(position.existingElement);
            } else if(position.insertion === 'append') {
                item.appendTo(position.existingElement);
            } else if(position.insertion === 'prepend') {
                item.prependTo(position.existingElement);
            }
        }

        if(content.type === 'text') {
            content = insertion_templates.find("div.content.html").clone();
            insertItem(content, position);
            content.attr('contenteditable', 'true').focus();
        } else if(content.type === 'image') {
            var image = insertion_templates.find("div.content.image").clone();
            insertItem(image, position);
            image.find("img").click();
        } else if(content.type === 'widget') {
            insertItem(content.widget, position);
        }
        resetControls();
    }

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
                resetControls();
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
            endCallback: resetControls,
        });
        $(this).tooltip('destroy'); // Just in case the browser doesn't trigger the mouseleave
        $(this).siblings("div.content-control").remove();
        $(this).remove();
    });

    // Choose crop ratio on 'crop-content' icon click
    var JcropApi;
    $(document).on('click', 'article div.crop-content', function(e) {
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
        var crop_control = insertion_templates.find("div.crop-control").clone().insertBefore(content);
        crop_control.data('original-content', content);
        crop_control.data('content-clone', content.clone());
        crop_control.offset({
            top: crop_control.offset().top - crop_control.outerHeight(),
            right: 0,
        });
        if(crop === undefined) {
            // Hide the controls by default for the first selection; until cropping selection has been made
            crop_control.find("div.submit").css('display', 'none');
        }

        $(this).siblings("div.content-control").tooltip('destroy').remove();
        $(this).tooltip('destroy').remove();

        // Default to free
        crop_control.find("div.choose-ratio button[data-ratio='free']").click();
    });

    $(document).on('click', 'article div.crop-control div.choose-ratio button', function() {
        var crop_control = $(this).parents("div.crop-control");
        var content = crop_control.data('original-content');
        var original_crop = JSON.parse(content.attr('data-json')).crop;
        var ratio = $(this).attr('data-ratio');
        var aspect_ratio;
        if(ratio !== 'free') {
            aspect_ratio = ratio.split(":")[0] / ratio.split(":")[1];
        }

        // Highlight the marked button
        $(this).siblings().removeClass('btn-danger');
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

        // Reapply the original selection to the cropper ui, if any
        if(original_crop !== undefined) {
            // In case we're cropping in a different column size, factor in the difference
            var image_width_ratio = content.width() / original_crop.width;
            var image_height_ratio = content.height() / original_crop.height;

            // Why does it take an array here, while it gives us an object in the event!? Tsk
            JcropApi.setSelect([
                original_crop.selection.x * image_width_ratio,
                original_crop.selection.y * image_height_ratio,
                original_crop.selection.x2 * image_width_ratio,
                original_crop.selection.y2 * image_height_ratio,
            ]);
        }
    });

    $(document).on('click', 'article div.crop-control div.submit button.use', function(e) {
        var crop_control = $(this).parents("div.crop-control");
        var original_content = crop_control.data('original-content');
        var original_image = original_content.find("img");
        var new_content = crop_control.data('content-clone');
        var new_image = new_content.find("img");
        var crop = JSON.parse(original_content.attr('data-json')).crop;

        if(crop === undefined) {
            $(this).siblings("button.remove").click();
            return $(this);
        }

        new_content.attr('data-json', original_content.attr('data-json'));
        new_content.insertAfter(crop_control);
        cropContent(new_content);
        endCropping(crop_control);
    });

    $(document).on('click', 'article div.crop-control div.submit button.remove', function(e) {
        var crop_control = $(this).parents("div.crop-control");
        var clone = crop_control.data('content-clone');
        var json = JSON.parse(clone.attr('data-json'));
        json.crop = undefined;
        clone.attr('data-json', JSON.stringify(json)).insertAfter(crop_control);
        endCropping(crop_control);
    });

    function endCropping(crop_control) {
        if(JcropApi !== undefined) {
            JcropApi.destroy();
            JcropApi = undefined;
        }
        crop_control.remove();
    }

    function cropContent(content) {
        ImageCropper.cropImage(
            JSON.parse(content.attr('data-json')).crop,
            content.find('img'),
            content,
            content.parents('div.column').width()
        );
        content.find('img').addClass('cropped');
    }

    // Change a row's column-structure
    $(document).on('click', article.selector + ' div.edit-structure button', function() {

        var row = $(this).parents("div.row-fluid").next("div[data-row]");

        if($(this).attr('data-type') === 'single') {
            var first_column = row.children("div.column").first();
            var extra_columns = row.children("div.column").slice(1);
            first_column.attr('class', '').addClass('column span12');

            extra_columns.each(function() {
                $(this).children().detach().appendTo(first_column);
            });
            extra_columns.remove();
        } else if($(this).attr('data-type') === 'double') {
            var first_column = row.children("div.column").first();
            var second_column = row.children("div.column").eq(1);
            var extra_columns = row.children("div.column").slice(2);

            if(second_column.length === 0) {
                second_column = $('<div></div>');
                second_column.insertAfter(first_column);
            }

            first_column.attr('class', '').addClass('column span6');
            second_column.attr('class', '').addClass('column span6');

            extra_columns.each(function() {
                $(this).children().detach().appendTo(second_column);
            });
            extra_columns.remove();
        } else if($(this).attr('data-type') === 'sidebar-left') {
            var first_column = row.children("div.column").first();
            var second_column = row.children("div.column").eq(1);
            var extra_columns = row.children("div.column").slice(2);

            if(second_column.length === 0) {
                second_column = $('<div></div>');
                second_column.insertAfter(first_column);
            }

            first_column.attr('class', '').addClass('column span3');
            second_column.attr('class', '').addClass('column span9');

            extra_columns.each(function() {
                $(this).children().detach().appendTo(second_column);
            });
            extra_columns.remove();
        } else if($(this).attr('data-type') === 'sidebar-right') {
            var first_column = row.children("div.column").first();
            var second_column = row.children("div.column").eq(1);
            var extra_columns = row.children("div.column").slice(2);

            if(second_column.length === 0) {
                second_column = $('<div></div>');
                second_column.insertAfter(first_column);
            }

            first_column.attr('class', '').addClass('column span9');
            second_column.attr('class', '').addClass('column span3');

            extra_columns.each(function() {
                $(this).children().detach().appendTo(second_column);
            });
            extra_columns.remove();
        } else if($(this).attr('data-type') === 'triple') {
            var first_column = row.children("div.column").first();
            var second_column = row.children("div.column").eq(1);
            var third_column = row.children("div.column").eq(2);
            var extra_columns = row.children("div.column").slice(3);

            if(second_column.length === 0) {
                second_column = $('<div></div>');
                second_column.insertAfter(first_column);
            }

            if(third_column.length === 0) {
                third_column = $('<div></div>');
                third_column.insertAfter(second_column);
            }

            first_column.attr('class', '').addClass('column span4');
            second_column.attr('class', '').addClass('column span4');
            third_column.attr('class', '').addClass('column span4');

            extra_columns.each(function() {
                $(this).children().detach().appendTo(third_column);
            });
            extra_columns.remove();
        } else if($(this).attr('data-type') === 'quadruple') {
            var first_column = row.children("div.column").first();
            var second_column = row.children("div.column").eq(1);
            var third_column = row.children("div.column").eq(2);
            var fourth_column = row.children("div.column").eq(3);
            var extra_columns = row.children("div.column").slice(4);

            if(second_column.length === 0) {
                second_column = $('<div></div>');
                second_column.insertAfter(first_column);
            }

            if(third_column.length === 0) {
                third_column = $('<div></div>');
                third_column.insertAfter(second_column);
            }

            if(fourth_column.length === 0) {
                fourth_column = $('<div></div>');
                fourth_column.insertAfter(third_column);
            }

            first_column.attr('class', '').addClass('column span3');
            second_column.attr('class', '').addClass('column span3');
            third_column.attr('class', '').addClass('column span3');
            fourth_column.attr('class', '').addClass('column span3');

            extra_columns.each(function() {
                $(this).children().detach().appendTo(fourth_column);
            });
            extra_columns.remove();
        }

        row.find("div.content.image").each(function() {
            if(JSON.parse($(this).attr('data-json')).crop !== undefined) {
                cropContent($(this));
            }
        });
        resetControls();
    });

    // Remove all editing-markup and re-build from scratch
    function resetControls() {

        // Remove all rows that are completely empty for content
        article.find("div[data-row]").each(function() {
            if($(this).find("div.column:has(div.content)").length === 0) {
                $(this).remove();
            }
        });

        // Remove existing editing-markups
        article.find("div.edit-structure,div.add-content,div.add-content-row").remove();

        var rows = article.find("div[data-row]");
        if(rows.length === 0) {
            // Edge case; if there are *no* rows
            insertion_templates.find("div.add-content-row").clone().prependTo(article);
        } else {
            // Iterate existing rows
            rows.each(function() {
                var columns = $(this).find("div.column");

                // If there is one great column, no nead for a trailing add column after last content
                // If there are several, we do want one
                var trailing_add_content = columns.length > 1;

                columns.each(function() {
                    insertion_templates.find("div.add-content").clone().prependTo($(this));
                    $(this).find("div.content").each(function() {
                        insertion_templates.find("div.add-content").clone().insertAfter($(this));
                    });
                    if(!trailing_add_content) {
                        $(this).children("div.add-content").last().remove();
                    }
                });
                insertion_templates.find("div.edit-structure").clone().insertBefore($(this));
                insertion_templates.find("div.add-content-row").clone().insertAfter($(this));
            });
        }

        // After each reset, add tooltips to the new button elements, the edit-structure buttons and add-content rows
        editor.find("div.content-choices button").tooltip();
        editor.find("div.edit-structure button").tooltip();
        editor.find("article div.add-content, article div.add-content-row").tooltip({placement: 'bottom'});
    }

    // Edit an existing widget
    $(document).on('click', 'article div.content.widget', function() {
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

            insertContent({type: 'widget', widget: widget}, position);
        }]);
    });

    // Global disable-iframes function
    window.disableIframes = disableIframes;
    function disableIframes(content) {
        // Can't capture click events in iframes, so replace them
        content.find("iframe").each(function() {
            var width = $(this).css('width');
            var height = $(this).css('height');
            var div = $('<div style="background: url(/static/img/iframe-placeholder.png) top left repeat; max-width: 100%">&nbsp;</div>');
            div.css('width', width);
            div.css('height', height);
            $(this).replaceWith(div);
        });
    }

    // Tags, used in the header for both pages and articles

    TagDisplay.enable({
        tagBox: $("div.editor-header div.tags div.tag-box"),
        pickerInput: $("div.editor-header div.tags input[name='tags']")
    });

    // Returns true if the given element position contains the given mouse coordinates
    function contains(element, mouseX, mouseY) {
        var objX = element.offset().left;
        var objY = element.offset().top;
        var objW = element.width();
        var objH = element.height();
        return mouseX >= objX && mouseX <= objX + objW && mouseY >= objY && mouseY <= objY + objH;
    }

});
