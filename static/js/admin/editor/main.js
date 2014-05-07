/* Common for page- and article-editor */
$(document).ready(function() {

    var editor = $("div.cms-editor");
    var article = editor.find("article");
    var insertion_templates = editor.find("div.insertion-templates");
    var add_button_modal = editor.find("div.add-button.modal");

    /**
     * Initialization
     */

    rangy.init();
    window.selection = undefined;
    var insertable;
    setEmpties();
    enableEditing();
    disableIframes($("article div.content.widget"));

    var toolbar = $("div.cms-editor-toolbar");
    var toolbarContents = toolbar.find("div.toolbar-contents");

    // An image currently being changed (need to save this state while opening the changer dialog)
    var currentImage;

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

    // Make toolbar draggable, but not if input-elements are clicked
    toolbar.draggable();
    toolbar.find("input,select,button,a").mousedown(function(e) {
        e.stopPropagation();
    });

    // Draggable will set position relative, so make sure it is fixed before the user drags it
    toolbar.css('position', 'fixed');

    /* Prevent all anchor clicks within the article */
    $(document).on('click', 'a', function(e) {
        if($(this).parents("article").length !== 0) {
            e.preventDefault();
        }
    });

    /* Highlight contenteditables that _are being edited_. */
    $(document).on('focus', 'article div.editable', function() {
        $(this).addClass('selected');
    });
    $(document).on('focusout', 'article div.editable', function() {
        $(this).removeClass('selected');
    });
    $(document).on('mouseup', 'article div.editable', setSelection);
    $(document).on('keyup', 'article div.editable', setSelection);
    function setSelection() {
        selection = rangy.getSelection();
    }

    /* Highlight empty html contents */
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
    $("article div.content.html, article div.content.lede").focusout();

    /* Hide completely empty image descriptions */
    $("article div.content.image").each(function() {
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

    /* Change image sources upon being clicked. */
    function changeImage() {

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
                removeContent(content);
            }
        });
    }

    // New method of adding content
    $(document).on('click', article.selector + ' div.add-content,' + article.selector + ' div.add-content-row', function() {
        $(this).addClass('active');
    });
    $(document).on('mouseleave', article.selector + ' div.add-content,' + article.selector + ' div.add-content-row', function() {
        $(this).removeClass('active');
    });

    $(document).on('click', article.selector + " div.add-content button", function() {
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

    $(document).on('click', article.selector + ' div.add-content-row button', function() {
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

    function insertContent(content, position) {
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

    function insertItem(item, position) {
        if(position.insertion === 'after') {
            item.insertAfter(position.existingElement);
        } else if(position.insertion === 'append') {
            item.appendTo(position.existingElement);
        } else if(position.insertion === 'prepend') {
            item.prependTo(position.existingElement);
        }
    }


    function resetControls() {

        // Remove all rows that are completely empty for content
        article.find("div[data-row]").each(function() {
            if($(this).find("div.column:has(div.content)").length === 0) {
                $(this).remove();
            }
        });

        article.find("div.edit-structure,div.add-content,div.add-content-row").remove();

        var rows = article.find("div[data-row]");

        // Edge case; if there are *no* rows
        if(rows.length === 0) {
            insertion_templates.find("div.add-content-row").clone().prependTo(article);
        } else {
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

        // After each reset, add tooltip to the new button elements
        editor.find("div.content-choices button").tooltip();

        // Add tooltip to the add-content rows
        editor.find("article div.add-content, article div.add-content-row").tooltip({placement: 'bottom'});
    }

    //
    // Initial edit-control states
    //

    resetControls();

    $(document).on('mouseenter', 'article div.content', function() {
        insertion_templates.find("div.remove-content").clone().appendTo($(this));
    });

    $(document).on('mouseleave', 'article div.content', function() {
        $(this).find("div.remove-content").remove();
    });

    $(document).on('click', 'article div.content div.remove-content a', function(e) {
        e.stopPropagation(); // Mostly to avoid click-event on an image
        $(this).parents("div.content").remove();
        resetControls();
    });

    //
    // Structure changes
    //

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

    // Remove content (text/image/widget)
    toolbar.find("button.remove-content").click(function() {
        function doneRemoving() {
            $(document).off('mouseenter mouseleave click', 'article div.content.html, article div.content.widget, article div.content.image');
            enableEditing();
            enableToolbar();
        }
        disableToolbar('Klikk på innholdet i artikkelen du vil ta bort...', doneRemoving);
        disableEditing();
        $(document).on('mouseenter', 'article div.content.html, article div.content.widget, article div.content.image', function() {
            $(this).addClass('hover-remove');
        }).on('mouseleave', 'article div.content.html, article div.content.widget, article div.content.image', function() {
            $(this).removeClass('hover-remove');
        }).on('click', 'article div.content.html, article div.content.widget, article div.content.image', function() {
            doneRemoving();
            var content = $(this);
            content.hide();
            var confirmation = $('<div class="alert alert-error"><p class="delete-content-warning">Er du sikker på at du vil fjerne dette elementet?</p><p><button class="btn btn-large btn-danger confirm"><i class="icon-warning-sign"></i> Ja, slett innholdet</button> <button class="btn btn-large cancel"><i class="icon-heart"></i> Nei, avbryt og ikke slett noe</button></p></div>');
            content.before(confirmation);
            confirmation.find("button.cancel").click(function() {
                confirmation.remove();
                content.show();
                content.removeClass('hover-remove');
                content.find(".editable").focusout();
                toolbar.find("button.cancel").click();
            });
            confirmation.find("button.confirm").click(function() {
                confirmation.remove();
                removeContent(content);
            });
        });
    });

    // Actually remove the content from DOM
    window.removeContent = removeContent;
    function removeContent(content) {
        if(content.siblings().length === 0) {
            setEmpty(content.parent());
        }
        content.remove();
    }


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

    /**
     * Structural changes (rows/columns)
     */

    // Add a new row with columns
    toolbar.find("button.add-columns").click(function() {
        disableToolbar("Velg hvor i artikkelen du vil legge til en ny rad...", function() {
            $(".insertable").remove();
        });
        insertables("Klikk her for å sette inn en rad", $("article"), function(event) {
            $("div.insert-columns").modal();
            insertable = $(this);
        });
    });

    $("div.insert-columns img[data-choice]").click(function() {
        $(this).parents("div.insert-columns").modal('hide');
        addColumns($(this).attr('data-choice'));
    });

    function addColumns(choice) {
        if(choice === "0") {
            columns = [{span: 12, offset: 0, order: 0}];
        } else if(choice === "1") {
            columns = [
                {span: 9, offset: 0, order: 0},
                {span: 3, offset: 0, order: 1}
            ];
        } else if(choice === "2") {
            columns = [
                {span: 6, offset: 0, order: 0},
                {span: 6, offset: 0, order: 1}
            ];
        } else if(choice === "3") {
            columns = [
                {span: 4, offset: 0, order: 0},
                {span: 4, offset: 0, order: 1},
                {span: 4, offset: 0, order: 2}
            ];
        } else if(choice === "4") {
            columns = [
                {span: 3, offset: 0, order: 0},
                {span: 3, offset: 0, order: 1},
                {span: 3, offset: 0, order: 2},
                {span: 3, offset: 0, order: 3}
            ];
        }
        var wrapper = $('<div class="row-fluid" data-row></div>');
        for(var i=0; i<columns.length; i++) {
            wrapper.append($('<div class="column span' + columns[i].span + ' offset' +
                columns[i].offset + '"></div>'));
        }
        var prev = insertable.prev();
        if(prev.length === 0) {
            insertable.parent().prepend(wrapper);
        } else {
            prev.after(wrapper);
        }
        wrapper.children().each(function() {
            setEmpty($(this));
        });
        $("article .insertable").remove();
        enableToolbar();
    }

    // Remove a row and all its content
    toolbar.find("button.remove-columns").click(function() {
        function doneRemoving() {
            $(document).off('mouseenter mouseleave click', 'article > div[data-row]');
            enableEditing();
            enableToolbar();
        }
        disableToolbar("Velg raden du vil fjerne...", doneRemoving);
        disableEditing();
        $(document).on('mouseenter', 'article > div[data-row]', function() {
            $(this).addClass('hover-remove');
        }).on('mouseleave', 'article > div[data-row]', function() {
            $(this).removeClass('hover-remove');
        }).on('click', 'article > div[data-row]', function() {
            var row = $(this);
            row.hide();
            doneRemoving();
            var confirmation = $('<div class="alert alert-error"><p class="delete-content-warning">Er du sikker på at du vil fjerne dette elementet?</p><p><button class="btn btn-large btn-danger confirm"><i class="icon-warning-sign"></i> Ja, slett innholdet</button> <button class="btn btn-large cancel"><i class="icon-heart"></i> Nei, avbryt og ikke slett noe</button></p></div>');
            row.before(confirmation);
            confirmation.find("button.cancel").click(function() {
                confirmation.remove();
                row.show();
                row.removeClass('hover-remove');
                row.find(".editable").focusout();
                toolbar.find("button.cancel").click();
            });
            confirmation.find("button.confirm").click(function() {
                confirmation.remove();
                row.remove();
                doneRemoving();
            });
        });
    });

    /**
     * Small, logical code snippets
     */

    /* Toggle toolbar usage */
    function disableToolbar(displayText, cancelCallback) {
        toolbarContents.hide();
        var btn = $('<button class="btn cancel">Avbryt</button>');
        btn.click(enableToolbar);
        btn.click(cancelCallback);
        toolbar.append('<p class="cancel">' + displayText + '</p>', btn);
    }
    function enableToolbar() {
        toolbar.find(".cancel").remove();
        toolbarContents.show();
    }

    /* Toggle editing of the actual content */
    window.disableEditing = disableEditing;
    function disableEditing() {
        $("article div.editable").removeAttr('contenteditable');
        $(document).off('click', 'article div.content.image');
    }
    window.enableEditing = enableEditing;
    function enableEditing() {
        $("article div.editable").attr('contenteditable', 'true');
        $(document).on('click', 'article div.content.image', changeImage);
    }

    /* Divs for inserting widgets/images/text */
    function insertables(text, container, click) {
        var well = $('<div class="insertable well">' + text + '</div>');
        well.click(click);
        var children = container.children();
        container.prepend(well);
        children.each(function() {
            well = well.clone(true);
            $(this).after(well);
        });
    }

    /* Show/remove placeholder text for empty columns */
    function setEmpty(column) {
        column.append('<div class="empty well">Tom kolonne</div>');
    }
    window.setEmpties = setEmpties;
    function setEmpties() {
        $("article .column").each(function() {
            if($(this).children(":not(.insertable)").length === 0) {
                setEmpty($(this));
            }
        });
    }
    window.removeEmpties = removeEmpties;
    function removeEmpties() {
        $("article .column").children("div.empty.well").remove();
    }

    window.disableIframes = disableIframes;
    function disableIframes(content) {
        // Can't capture click events in iframes, so replace them
        content.find("iframe").each(function() {
            var width = $(this).css('width');
            var height = $(this).css('height');
            var div = $('<div style="background: url(/static/img/iframe-placeholder.png) top left repeat">&nbsp;</div>');
            div.css('width', width);
            div.css('height', height);
            $(this).replaceWith(div);
        });
    }

    /* Tags, used for both pages and articles */

    TagDisplay.enable({
        tagBox: $("div.editor-header div.tags div.tag-box"),
        pickerInput: $("div.editor-header div.tags input[name='tags']")
    });

});
