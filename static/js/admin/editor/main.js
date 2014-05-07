/* The main CMS editor functionality */

$(function() {

    var editor = $("div.cms-editor");
    var article = editor.find("article");
    var insertion_templates = editor.find("div.insertion-templates");
    var add_button_modal = editor.find("div.add-button.modal");
    var toolbar = editor.find("div.cms-editor-toolbar");
    var toolbarContents = toolbar.find("div.toolbar-contents");

    //
    // Initialization
    //

    rangy.init();
    window.selection = undefined;
    disableIframes(article.find("div.content.widget"));
    resetControls();

    // An image currently being changed (need to save this state while opening the changer dialog)
    var currentImage;

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
        $(this).attr('contenteditable', true);
        $(this).focus();
    });
    $(document).on('focusout', 'article div.content.html, article div.content.lede', function() {
        if($(this).text().trim() === "" && $(this).children("hr").length === 0) {
            $(this).addClass('empty');
            $(this).focus(function() {
                $(this).removeClass('empty');
            });
            $(this).removeAttr('contenteditable');
            $(this).attr('data-placeholder', true);
            if($(this).hasClass('html')) {
                $(this).text("Klikk for å legge til tekst...");
            } else if($(this).hasClass('lede')) {
                $(this).text("Klikk for å legge til ingress...");
            }
        }
    });

    // Hide completely empty image descriptions
    article.find("div.content.image").each(function() {
        var content = $(this);
        hidePictureText(content);
    });

    function hidePictureText(content){
        var description = content.find("span.description").text();
        var photographer = content.find("span.photographer span.content").text();

        if(description === '' && photographer === ''){
            content.find("div.img-desc").hide();
        }else{
            content.find("div.img-desc").show();
        }

        if(description === '') {
            content.find("span.description").hide();
        } else {
            content.find("span.description").show();
        }

        if(photographer === '') {
            content.find("span.photographer").hide();
        } else {
            content.find("span.photographer").show();
        }
    }

    // Change image sources upon being clicked
    $(document).on('click', 'article div.content.image', function() {
        currentImage = $(this).find("img");
        var content = $(this);
        var currentDescription = content.find("span.description");
        var currentPhotographer = content.find("span.photographer span.content");
        var anchor = $(this).find("a").attr('href');
        if(anchor === undefined) {
            anchor = '';
        }
        ImageDialog.openImageDialog({
            image: currentImage,
            anchor: anchor,
            description: currentDescription.text(),
            photographer: currentPhotographer.text(),
            save: function(src, anchor, description, photographer) {
                if(anchor.length === 0) {
                    // No link
                    if(currentImage.parent("a").length > 0) {
                        // *Was* link, but is now removed
                        currentImage.parent().before(currentImage).remove();
                    }
                } else {
                    // Add link
                    if(currentImage.parent("a").length > 0) {
                        // Link exists, update it
                        currentImage.parent().attr('href', anchor);
                    } else {
                        // No existing link, add it
                        var anchorEl = $('<a href="' + anchor + '"></a>');
                        currentImage.before(anchorEl).detach();
                        anchorEl.prepend(currentImage);
                    }
                }
                currentImage.attr('src', src);
                currentImage.attr('alt', description);

                currentDescription.text(description);
                currentPhotographer.text(photographer);
                hidePictureText(content);

            },
            remove: function() {
                content.remove();
                resetControls();
            }
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
            var new_row = $('<div class="row-fluid" data-row><div class="column span12"></div></div>');
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
            image.css("overflow", "hidden");
            insertItem(image, position);
            image.find("img").click();
        } else if(content.type === 'widget') {
            insertItem(content.widget, position);
        } else if(content.type === 'button') {
            add_button_modal.modal();
        }
        resetControls();
    }

    // Show 'remove-content' icon upon hovering content
    $(document).on('mouseenter', 'article div.content', function() {
        insertion_templates.find("div.remove-content").clone().appendTo($(this)).tooltip();
    });

    // Cancel the 'remove-content' icon upon mouse leave
    $(document).on('mouseleave', 'article div.content', function() {
        $(this).find("div.remove-content").remove();
    });

    // Confirm and remove content when 'remove-content' icon clicked
    $(document).on('click', 'article div.content div.remove-content', function(e) {
        e.stopPropagation(); // Avoid click-event on an image or widget
        if(confirm($(this).attr('data-confirm'))) {
            $(this).parents("div.content").remove();
            resetControls();
        }
    });

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
                        $(this).children().last().remove();
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

    // Insert custom button
    add_button_modal.find("div.alert").hide();
    add_button_modal.on('show', function(event) {
        if(selection === undefined) {
            alert('Trykk på tekstelementet du vil legge til knappen i først, og prøv igjen.');
            $(this).on('shown', function() {
                $(this).modal('hide');
            });
        }
    });
    add_button_modal.find("button.insert").click(function() {
        var text = add_button_modal.find("input[name='text']").val();
        var url = add_button_modal.find("input[name='url']").val().trim();
        if(text === "") {
            add_button_modal.find("div.alert").show();
            return;
        }
        var el;
        if(url !== "") {
            if(!url.match(/^https?:\/\//)) {
                url = "http://" + url;
            }
            el = 'a href="' + url + '"';
        } else {
            el = 'button';
        }
        var button = $('<' + el + ' class="btn">' + text + '</' + el + '>');
        button.addClass(add_button_modal.find("input[name='color']:checked").val())
              .addClass(add_button_modal.find("input[name='size']:checked").val());
        $(selection.anchorNode).parents(".editable").append($('<p></p>').prepend(button), $('<p><br></p>'));
        add_button_modal.modal('hide');
    });
    add_button_modal.find("table.choices button").click(function() {
        $(this).parent().prev().children("input[type='radio']").click();
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

});
