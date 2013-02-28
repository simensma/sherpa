/* Common for advanced- and article-editor */
$(document).ready(function() {

    /**
     * Initialization
     */

    rangy.init();
    window.selection;
    var insertable;
    setEmpties();
    enableEditing();
    disableIframes($("article div.content.widget"));

    // An image currently being changed (need to save this state while opening the changer dialog)
    var currentImage;

    // Make toolbar draggable
    $("#toolbar").draggable({
        containment: 'window'
    });

    // Draggable will set position relative, so make sure it is fixed before the user drags it
    $("#toolbar").css('position', 'fixed');

    /* Prevent all anchor clicks within the article */
    $(document).on('click', 'a', function(e) {
        if($(this).parents("article").length != 0) {
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
        if($(this).text().trim() === "" && $(this).children("hr").length == 0) {
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

        if(description == '' && photographer == ''){
            content.find("div.img-desc").hide();
        }else{
            content.find("div.img-desc").show();
        }

        if(description == '') {
            content.find("span.description").hide();
        } else {
            content.find("span.description").show();
        }

        if(photographer == '') {
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
        openImageDialog(currentImage, anchor, currentDescription.text(), currentPhotographer.text(), function(src, anchor, description, photographer) {

            if(anchor.length == 0) {
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

        }, function() {
            removeContent(content);
        });
    }

    //Content changes (text, images, widgets)
    var noStructureForContentWarning = "Det er ingen rader/kolonner å sette inn innhold i! " +
        "Gå til 'struktur'-knappen først, og legg til noen rader og kolonner.";

    // Add text
    $("#toolbar button.add-text").click(function() {
        if($("article").children().length == 0) {
            alert(noStructureForContentWarning);
            return;
        }
        removeEmpties();
        disableToolbar("Klikk på et ledig felt i artikkelen for å legge til tekst...", function() {
            $("article .insertable").remove();
            setEmpties();
        });
        insertables("Klikk for å legge til tekst her", $("article .column"), function(event) {
            var content = $("div.insertion-templates div.content.html").clone();
            content.insertAfter($(event.target));
            refreshSort();
            setEmpties();
            enableToolbar();
            $("article .insertable").remove();
            if(sortState == 'formatting') {
                content.attr('contenteditable', 'true').focus();
            } else {
                content.trigger('focusout');
            }
        });
    });

    // Add image
    $("#toolbar a.button.image").click(function() {
        if($("article").children().length == 0) {
            alert(noStructureForContentWarning);
            return;
        }
        removeEmpties();
        disableToolbar("Klikk på et ledig felt i artikkelen for å legge til bilde...", function() {
            $("article .insertable").remove();
            setEmpties();
        });
        insertables("Klikk for å legge til bilde her", $("article .column"), function(event) {
            var image = $("div.insertion-templates div.content.image").clone();
            image.css("overflow", "hidden");
            image.insertAfter($(event.target));
            image.find("img").click();
            refreshSort();
            setEmpties();
            $("article .insertable").remove();
            enableToolbar();
        });
    });

    // Add widget
    window.widgetPosition; // Set when inserting a new widget
    window.widgetBeingEdited; // If undefined: a new widget, if defined: the widget being edited
    $("#toolbar a.button.widget").click(function() {
        if($("article").children().length == 0) {
            alert(noStructureForContentWarning);
            return;
        }
        removeEmpties();
        disableToolbar("Klikk på et ledig felt i artikkelen for å legge til widget...", function() {
            $("article .insertable").remove();
            setEmpties();
        });
        insertables("Klikk for å legge til widget her", $("article .column"), function() {
            $("div.add-widget").modal();
            enableToolbar();
            widgetPosition = {
                prev: $(this).prev(),
                parent: $(this).parent()
            };
            $("article .insertable").remove();
            enableToolbar();
        });
    });
    $("div.add-widget div.widget-thumbnail").click(function() {
        widgetBeingEdited = undefined;
        $(this).parents("div.add-widget").modal('hide');
        $(document).trigger('widget.new.' + $(this).attr('data-widget'));
    });

    // Remove content (text/image/widget)
    $("#toolbar button.remove-content").click(function() {
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
                $("#toolbar button.cancel").click();
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
        if(content.siblings().length == 0) {
            setEmpty(content.parent());
        }
        content.remove();
        refreshSort();
    }


    // Insert custom button
    $("button.insert-button").click(function() {
        $("div.add-button").modal();
    });
    $("div.add-button div.alert").hide();
    $("div.add-button").on('show', function(event) {
        if(typeof selection === 'undefined') {
            alert('Trykk på tekstelementet du vil legge til knappen i først, og prøv igjen.');
            $(this).on('shown', function() {
                $(this).modal('hide');
            });
        }
    });
    $("div.add-button button.insert").click(function() {
        var text = $("div.add-button input[name='text']").val();
        var url = $("div.add-button input[name='url']").val().trim();
        if(text == "") {
            $("div.add-button div.alert").show();
            return;
        }
        var el;
        if(url != "") {
            if(!url.match(/^https?:\/\//)) {
                url = "http://" + url;
            }
            el = 'a href="' + url + '"';
        } else {
            el = 'button';
        }
        var button = $('<' + el + ' class="btn">' + text + '</' + el + '>');
        button.addClass($("div.add-button input[name='color']:checked").val())
              .addClass($("div.add-button input[name='size']:checked").val());
        $(selection.anchorNode).parents(".editable").append($('<p></p>').prepend(button), $('<p><br></p>'));
        $("div.add-button").modal('hide');
    });
    $("div.add-button table.choices button").click(function() {
        $(this).parent().prev().children("input[type='radio']").click();
    });

    /**
     * Structural changes (rows/columns)
     */

    // Add a new row with columns
    $("#toolbar button.add-columns").click(function() {
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
        if(choice == 0) {
            columns = [{span: 12, offset: 0, order: 0}]
        } else if(choice == 1) {
            columns = [{span: 9, offset: 0, order: 0},
                       {span: 3, offset: 0, order: 1}]
        } else if(choice == 2) {
            columns = [{span: 6, offset: 0, order: 0},
                       {span: 6, offset: 0, order: 1}]
        } else if(choice == 3) {
            columns = [{span: 4, offset: 0, order: 0},
                       {span: 4, offset: 0, order: 1},
                       {span: 4, offset: 0, order: 2}]
        } else if(choice == 4) {
            columns = [{span: 3, offset: 0, order: 0},
                       {span: 3, offset: 0, order: 1},
                       {span: 3, offset: 0, order: 2},
                       {span: 3, offset: 0, order: 3}]
        }
        var order = insertable.prevAll(":not(.insertable)").length;
        $.ajaxQueue({
            url: '/sherpa/cms/kolonner/ny/',
            data: "version=" + encodeURIComponent($("div.editor-header").attr("data-version-id")) +
                  "&order=" + encodeURIComponent(order) +
                  "&columns=" + encodeURIComponent(JSON.stringify(columns))
        }).done(function(result) {
            var wrapper = $('<div class="row-fluid"></div>');
            for(var i=0; i<columns.length; i++) {
                wrapper.append($('<div class="column span' + columns[i].span + ' offset' +
                    columns[i].offset + '"></div>'));
            }
            var prev = insertable.prev();
            if(prev.length == 0) {
                insertable.parent().prepend(wrapper);
            } else {
                prev.after(wrapper);
            }
            var ids = JSON.parse(result);
            wrapper.attr("data-id", ids[0]);
            var i = 1;
            wrapper.children().each(function() {
                $(this).attr("data-id", ids[i++]);
                setEmpty($(this));
            });
            wrapper.sortable({disabled: true});
            refreshSort();
        }).fail(function(result) {
            // Todo
        }).always(function(result) {
            $("article .insertable").remove();
            disableOverlay();
            enableToolbar();
        });
    }

    // Remove a row and all its content
    $("#toolbar button.remove-columns").click(function() {
        function doneRemoving() {
            $(document).off('mouseenter mouseleave click', 'article > div.row-fluid');
            enableEditing();
            enableToolbar();
        }
        disableToolbar("Velg raden du vil fjerne...", doneRemoving);
        disableEditing();
        $(document).on('mouseenter', 'article > div.row-fluid', function() {
            $(this).addClass('hover-remove');
        }).on('mouseleave', 'article > div.row-fluid', function() {
            $(this).removeClass('hover-remove');
        }).on('click', 'article > div.row-fluid', function() {
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
                $("#toolbar button.cancel").click();
            });
            confirmation.find("button.confirm").click(function() {
                confirmation.remove();
                enableOverlay();
                $.ajaxQueue({
                    url: '/sherpa/cms/rad/slett/' + encodeURIComponent(row.attr('data-id')) + '/',
                    type: 'POST'
                }).done(function(result) {
                    row.remove();
                }).fail(function(result) {
                    // Todo
                }).always(function(result) {
                    refreshSort();
                    doneRemoving();
                    disableOverlay();
                });
            });
        });
    });

    // Change edit mode - formatting, swap rows, swap columns
    var sortState = 'formatting';
    $("article").sortable({ disabled: true });
    $("article > div.row-fluid").sortable({ disabled: true });
    $("#toolbar button.formatting").button('toggle');

    $("#toolbar button.formatting").click(function() {
        disableSort($("article"));
        disableSort($("article > div.row-fluid"));
        $("article .editable").attr('contenteditable', 'true');
        sortState = 'formatting';
    });

    $("#toolbar button.horizontal").click(function() {
        disableSort($("article"));
        enableSort($("article > div.row-fluid"), 'horizontal');
        $("article .editable").removeAttr('contenteditable');
        sortState = 'horizontal';
    });

    $("#toolbar button.vertical").click(function() {
        enableSort($("article"), 'vertical');
        disableSort($("article > div.row-fluid"));
        $("article .editable").removeAttr('contenteditable');
        sortState = 'vertical';
    });

    function disableSort(el) {
        el.sortable('disable');
        el.children().off('mouseenter');
        el.children().off('mouseleave');
    }

    function enableSort(el, alignment) {
        el.sortable('enable');
        el.children().on('mouseenter', function() {
            $(this).addClass('moveable ' + alignment);
        });
        el.children().on('mouseleave', function() {
            $(this).removeClass('moveable ' + alignment);
        });
    }

    window.refreshSort = refreshSort;
    function refreshSort() {
        $("article").sortable('refresh');
        $("article > div.row-fluid").sortable('refresh');
        if(sortState == 'vertical') {
            enableSort($("article"), sortState);
        } else if(sortState == 'horizontal') {
            enableSort($("article > div.row-fluid"), sortState);
        }
    }

    /**
     * Small, logical code snippets
     */

    /* Toggle overlay for the entire site */
    window.enableOverlay = enableOverlay;
    function enableOverlay() {
        $("<div class=\"ui-widget-overlay\"></div>").appendTo('body');
        $("<div class=\"overlay-loader\"><h3>Lagrer, vennligst vent...</h3><p><img src=\"/static/img/ajax-loader-large.gif\" alt=\"Lagrer, vennligst vent...\"></p></div>")
          .appendTo('body');
    }
    window.disableOverlay = disableOverlay;
    function disableOverlay() {
        $(".ui-widget-overlay,.overlay-loader").remove();
    }

    /* Toggle toolbar usage */
    function disableToolbar(displayText, cancelCallback) {
        $("#toolbar *").hide();
        var btn = $('<button class="btn cancel">Avbryt</button>');
        btn.click(enableToolbar);
        btn.click(cancelCallback);
        $("#toolbar").append('<p class="cancel">' + displayText + '</p>', btn);
    }
    function enableToolbar() {
        $("#toolbar .cancel").remove();
        $("#toolbar *").show();
    }

    /* Toggle editing of the actual content */
    window.disableEditing = disableEditing;
    function disableEditing() {
        $("article div.editable").removeAttr('contenteditable');
        $(document).off('click', 'article div.content.image');
        $(document).off('click', 'article div.content.widget');
    }
    window.enableEditing = enableEditing;
    function enableEditing() {
        $("article div.editable").attr('contenteditable', 'true');
        $(document).on('click', 'article div.content.widget', function() {
            $(this).trigger('widget.edit');
        });
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
            if($(this).children(":not(.insertable)").length == 0) {
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

    // Create the tagger object, make it globally accessible (save.js will use this)
    window.cms_tagger = new TypicalTagger($("div.editor-header div.tags input[name='tags']"), $("div.editor-header div.tags div.tag-box"));

    // Collect existing tags based on the DOM and layout
    var tags = [];
    $("div.editor-header div.tags div.tag").each(function() {
        tags.push($(this).text().trim());
    });
    cms_tagger.tags = tags;


});
