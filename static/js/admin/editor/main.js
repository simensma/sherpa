/* Common for advanced- and article-editor */
$(document).ready(function() {

    /**
     * Initialization
     */

    rangy.init();
    window.selection;
    var insertable;
    $("div.no-save-warning").hide();
    setEmpties();
    enableEditing();
    disableIframes($("article div.widget"));

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

    /* Hide empty image photographer description */
    $("article div.image span.photographer").each(function() {
        if($(this).children("span.content").text() == "") {
            $(this).hide();
        }
    });

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
        openImageDialog(currentImage.attr('src'), anchor, currentDescription.text(), currentPhotographer.text(), function(src, anchor, description, photographer) {
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
            debugger;
            currentDescription.text(description);
            currentPhotographer.text(photographer);
            if(photographer == '') {
                currentPhotographer.parent("span.photographer").hide();
            } else {
                currentPhotographer.parent("span.photographer").show();
            }
            $("div.editor-header div.save button.save").click();
        }, function() {
            $.ajax({
                url: '/sherpa/cms/innhold/slett/' + encodeURIComponent(content.attr('data-id')) + '/',
                type: 'POST'
            }).done(function(result) {
                if(content.siblings().length == 0) {
                    setEmpty(content.parent());
                }
                content.remove();
            }).fail(function(result) {
                // Todo
            }).always(function(result) {
                refreshSort();
                doneRemoving();
                disableOverlay();
            });
        });
    }

    /**
     * Content changes (text, images, widgets)
     */

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
            var html = $('<p><br></p>');
            function done(wrapper) {
                if(sortState == 'formatting') {
                    wrapper.attr('contenteditable', 'true').focus();
                }
                refreshSort();
                setEmpties();
                wrapper.click();
                wrapper.focus();
                $("article .insertable").remove();
            }
            addContent($(event.target).prev(), $(event.target).parent(),
                $(event.target).parent(".column").attr("data-id"),
                $(event.target).prevAll(":not(.insertable)").length,
                $("<div/>").append(html).html(), 'html', done);
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
            var image = $('<img src="" alt=""><div class="img-desc"><span class="description"></span><span class="photographer">Foto: <span class="content"></span>');
            function imageDone(wrapper) {
                var image = wrapper.find("img");
                image.click();
                refreshSort();
                setEmpties();
                $("article .insertable").remove();
            }
            addContent($(event.target).prev(), $(event.target).parent(),
                $(event.target).parent(".column").attr("data-id"),
                $(event.target).prevAll(":not(.insertable)").length,
                $("<div/>").append(image).html(), 'image', imageDone);
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
            $("#dialog-add-widget").dialog('open');
            enableToolbar();
            widgetPosition = {
                prev: $(this).prev(),
                parent: $(this).parent(),
                column: $(this).parent(".column").attr("data-id"),
                order: $(this).prevAll(":not(.insertable)").length
            };
            $("article .insertable").remove();
            setEmpties();
        });
    });
    $("#dialog-add-widget div.widget-thumbnail").click(function() {
        widgetBeingEdited = undefined;
        $(this).parents("#dialog-add-widget").dialog('close');
        $("div.widget-edit input[type='text'], div.widget-edit textarea").val('');
        $("div.dialog.widget-edit[data-widget='" + $(this).attr('data-widget') + "']").dialog('open');
    });

    // Remove content (text/image/widget)
    $("#toolbar button.remove-content").click(function() {
        function doneRemoving() {
            $(document).off('mouseenter mouseleave click');
            enableEditing();
            enableToolbar();
        }
        disableToolbar('Klikk på innholdet i artikkelen du vil ta bort...', doneRemoving);
        disableEditing();
        $(document).on('mouseenter', 'div.html, div.widget:not(.static), div.image', function() {
            $(this).addClass('hover-remove');
        }).on('mouseleave', 'div.html, div.widget:not(.static), div.image', function() {
            $(this).removeClass('hover-remove');
        }).on('click', 'div.html, div.widget:not(.static), div.image', function() {
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
                enableOverlay();
                $.ajax({
                    url: '/sherpa/cms/innhold/slett/' + encodeURIComponent(content.attr('data-id')) + '/',
                    type: 'POST'
                }).done(function(result) {
                    if(content.siblings().length == 0) {
                        setEmpty(content.parent());
                    }
                    content.remove();
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

    // Insert custom button
    $("div#dialog-add-button div.alert").hide();
    $("div#dialog-add-button").bind('dialogopen', function(event, ui) {
        if(selection === undefined) {
            $(this).dialog('close');
            alert('Trykk på tekstelementet du vil legge til knappen i først, og prøv igjen.');
        }
    });
    $("div#dialog-add-button button.insert").click(function() {
        var text = $("div#dialog-add-button input[name='text']").val();
        var url = $("div#dialog-add-button input[name='url']").val();
        if(text == "") {
            $("div#dialog-add-button div.alert").show();
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
        button.addClass($("div#dialog-add-button input[name='color']:checked").val())
              .addClass($("div#dialog-add-button input[name='size']:checked").val());
        $(selection.anchorNode).parents(".editable").append($('<p></p>').prepend(button), $('<p><br></p>'));
        $("div#dialog-add-button").dialog('close');
    });
    $("div#dialog-add-button table.choices button").click(function() {
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
            $("#dialog-columns").dialog('open');
            insertable = $(this);
        });
    });

    $("#dialog-columns img").click(function() {
        $(this).parents("#dialog-columns").dialog('close');
    });
    $("#dialog-columns img.full").click(function() {
        addColumns(0);
    });
    $("#dialog-columns img.sidebar").click(function() {
        addColumns(1);
    });
    $("#dialog-columns img.two").click(function() {
        addColumns(2);
    });
    $("#dialog-columns img.three").click(function() {
        addColumns(3);
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
        }
        var order = insertable.prevAll(":not(.insertable)").length;
        $.ajax({
            url: '/sherpa/cms/kolonner/ny/',
            type: 'POST',
            data: "version=" + encodeURIComponent($("article").attr("data-id")) +
                  "&order=" + encodeURIComponent(order) +
                  "&columns=" + encodeURIComponent(JSON.stringify(columns))
        }).done(function(result) {
            var wrapper = $('<div class="row"></div>');
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
            $(document).off('mouseenter mouseleave click', 'article .row');
            enableEditing();
            enableToolbar();
        }
        disableToolbar("Velg raden du vil fjerne...", doneRemoving);
        disableEditing();
        $(document).on('mouseenter', 'article .row', function() {
            $(this).addClass('hover-remove');
        }).on('mouseleave', 'article .row', function() {
            $(this).removeClass('hover-remove');
        }).on('click', 'article .row', function() {
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
                $.ajax({
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
    $("article .row").sortable({ disabled: true });
    $("#toolbar button.formatting").button('toggle');

    $("#toolbar button.formatting").click(function() {
        disableSort($("article"));
        disableSort($("article .row"));
        $("article .editable").attr('contenteditable', 'true');
        sortState = 'formatting';
    });

    $("#toolbar button.horizontal").click(function() {
        disableSort($("article"));
        enableSort($("article .row"), 'horizontal');
        $("article .editable").removeAttr('contenteditable');
        sortState = 'horizontal';
    });

    $("#toolbar button.vertical").click(function() {
        enableSort($("article"), 'vertical');
        disableSort($("article .row"));
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
        $("article .row").sortable('refresh');
        if(sortState == 'vertical') {
            enableSort($("article"), sortState);
        } else if(sortState == 'horizontal') {
            enableSort($("article .row"), sortState);
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
        $("article div.image img").off('click focus focusout');
        $(document).off('click', 'div.widget');
    }
    window.enableEditing = enableEditing;
    function enableEditing() {
        $("article div.editable").attr('contenteditable', 'true');
        $(document).on('click', 'div.widget', editWidget);
        $(document).on('click', 'div.image', changeImage);
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

    /**
     * Major DOM changes.
     * Typically includes an ajax request and,
     * depending on the result, DOM manipulation.
     */

    /* Add content-objects to some column */
    window.addContent = addContent;
    function addContent(prev, parent, column, order, content, type, done) {
        enableOverlay();
        $.ajax({
            url: '/sherpa/cms/innhold/ny/',
            type: 'POST',
            data: "column=" + encodeURIComponent(column) +
                  "&order=" + encodeURIComponent(order) +
                  "&content=" + encodeURIComponent(content) +
                  "&type=" + encodeURIComponent(type)
        }).done(function(result) {
            result = JSON.parse(result);
            var editable = '';
            if(type == 'html' || type == 'title' || type == 'lede') {
                editable = ' editable';
            }
            var wrapper = $('<div class="content ' + type + editable + '" data-id="' + result.id + '"></div>').append(result.content);
            if(result.json !== undefined) {
                wrapper.attr('data-json', result.json);
            }
            if(prev.length == 0) {
                parent.prepend(wrapper);
            } else {
                prev.after(wrapper);
            }
            if(type == 'widget') {
                disableIframes(wrapper);
            }
            // Disable the overlay _before_ calling the provided 'done' function
            disableOverlay();
            done(wrapper);
        }).fail(function(result) {
            // Todo
            disableOverlay();
            $(document.body).html(result.responseText);
        }).always(function(result) {
            enableToolbar();
        });
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

});
