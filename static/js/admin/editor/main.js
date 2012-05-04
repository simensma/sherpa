/* Common for avanced- and article-editor */
$(document).ready(function() {

    /**
     * Initialization
     */

    rangy.init();
    var selection;
    var insertable;
    $("div.no-save-warning").hide();
    setEmpties();
    enableEditing();
    autoRemoveEmptyContent($("article .html[data-type!='lede']"));

    // An image currently being changed (need to save this state while opening the changer dialog)
    var currentImage;

    // Make toolbar draggable
    $("#toolbar").draggable({
        containment: 'window'
    });

    // Draggable will set position relative, so make sure it is fixed before the user drags it
    $("#toolbar").css('position', 'fixed');


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
                selectableContent(wrapper);
                autoRemoveEmptyContent(wrapper);
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
    $("#toolbar button.add-image").click(function() {
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
            /* Sorry, this doesn't look very pretty.
             * First add the image content, then AFTER it's added (in the 'done' function
             * of the image) add the html content (text below image).
             */
            var image = $('<img src="" alt="">');
            var html = $('<p>BILDETEKST: Donec ut libero sed arcu vehicula.<br><em>Foto: Kari Nordmann/DNT</em></p>');
            function imageDone(wrapper) {
                var image = wrapper.find("img");
                function contentDone(wrapper) {
                    changeableImages(image);
                    image.click();
                    selectableContent(wrapper);
                    autoRemoveEmptyContent(wrapper);
                    if(sortState == 'formatting') {
                        wrapper.attr('contenteditable', 'true');
                    }
                    refreshSort();
                    setEmpties();
                    $("article .insertable").remove();
                }
                addContent($(event.target).prev(), $(event.target).parent(),
                    $(event.target).parent(".column").attr("data-id"),
                    $(event.target).prevAll(":not(.insertable)").length,
                    $("<div/>").append(html).html(), 'html', contentDone);
            }
            addContent($(event.target).prev(), $(event.target).parent(),
                $(event.target).parent(".column").attr("data-id"),
                $(event.target).prevAll(":not(.insertable)").length,
                $("<div/>").append(image).html(), 'image', imageDone);
        });
    });

    // Add widget
    var widgetPosition; // Set when inserting a new widget
    var widgetBeingEdited; // If undefined: a new widget, if defined: the widget being edited

    $("#toolbar button.add-widget").click(function() {
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
        widgetBeingEdited = undefined; // Defined in widgets.js
        $(this).parents("#dialog-add-widget").dialog('close');
        $("div.widget-edit input[type='text'], div.widget-edit textarea").val('');
        $("div.dialog.widget-edit." + $(this).attr('data-widget')).dialog('open');
    });

    // Remove content (text/image/widget)
    $("#toolbar button.remove-content").click(function() {
        function doneRemoving() {
            $("article div.html, article div.widget, article div.image").off('hover click');
            enableEditing();
            enableToolbar();
        }
        disableToolbar('Klikk på innholdet i artikkelen du vil ta bort...', doneRemoving);
        disableEditing();
        $("article div.html, article div.widget, article div.image").hover(function() {
            $(this).addClass('hover-remove');
        }, function() {
            $(this).removeClass('hover-remove');
        }).click(function() {
            doneRemoving();
            var content = $(this);
            content.hide();
            var confirmation = $('<div class="alert alert-danger"><p class="delete-content-warning">Er du sikker på at du vil fjerne dette elementet?</p><p><button class="btn btn-large btn-danger confirm"><i class="icon-warning-sign"></i> Ja, slett innholdet</button> <button class="btn btn-large cancel"><i class="icon-heart"></i> Nei, avbryt og ikke slett noe</button></p></div>');
            content.before(confirmation);
            confirmation.find("button.cancel").click(function() {
                confirmation.remove();
                content.show();
                content.removeClass('hover-remove');
                content.find(".html").focusout();
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
        $(selection.anchorNode).parents(".html").append($('<p></p>').prepend(button), $('<p><br></p>'));
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
    })
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
    $("#toolbar .tab-pane.structure button.remove-columns").click(function() {
        function doneRemoving() {
            enableEditing();
            enableToolbar();
            $("article .row").off('hover click');
        }
        disableToolbar("Velg raden du vil fjerne...", doneRemoving);
        disableEditing();
        $("article .row").hover(function() {
            $(this).addClass('hover-remove');
        }, function() {
            $(this).removeClass('hover-remove');
        }).click(function() {
            var row = $(this);
            row.hide();
            doneRemoving();
            var confirmation = $('<div class="alert alert-danger"><p class="delete-content-warning">Er du sikker på at du vil fjerne dette elementet?</p><p><button class="btn btn-large btn-danger confirm"><i class="icon-warning-sign"></i> Ja, slett innholdet</button> <button class="btn btn-large cancel"><i class="icon-heart"></i> Nei, avbryt og ikke slett noe</button></p></div>');
            row.before(confirmation);
            confirmation.find("button.cancel").click(function() {
                confirmation.remove();
                row.show();
                row.removeClass('hover-remove');
                row.find(".html").focusout();
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
    $("#toolbar .structure button.formatting").button('toggle');

    $("#toolbar .structure button.formatting").click(function() {
        disableSort($("article"));
        disableSort($("article .row"));
        $("article .html").attr('contenteditable', 'true');
        sortState = 'formatting';
    });

    $("#toolbar .structure button.horizontal").click(function() {
        disableSort($("article"));
        enableSort($("article .row"), 'horizontal');
        $("article .html").removeAttr('contenteditable');
        sortState = 'horizontal';
    });

    $("#toolbar .structure button.vertical").click(function() {
        enableSort($("article"), 'vertical');
        disableSort($("article .row"));
        $("article .html").removeAttr('contenteditable');
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
     * Toolbar buttons
     */
    $("#toolbar div.formatting a.button").each(function() {
        $(this).css('background-image', 'url(' + $(this).attr('data-image') + '-inactive.png)');
    });
    $("#toolbar div.formatting a.button").hover(function() {
        $(this).css('background-image', 'url(' + $(this).attr('data-image') + '-hover.png)');
    }, function() {
        $(this).css('background-image', 'url(' + $(this).attr('data-image') + '-inactive.png)');
    }).mousedown(function() {
        $(this).css('background-image', 'url(' + $(this).attr('data-image') + '-active.png)');
    }).mouseup(function() {
        $(this).css('background-image', 'url(' + $(this).attr('data-image') + '-hover.png)');
    });

    $("#toolbar select").change(function() {
        $("select option:selected").each(function() {
            // The smart thing to do here would be:
            // document.execCommand('formatblock', false, $(this).val());
            // But IE doesn't support that, so. FML.
            var node = $(selection.anchorNode).parent();
            node.replaceWith($('<' + $(this).val() + '></' + $(this).val() + '>').prepend(node.contents()));
        });
        $("#toolbar select").val("default");
    });
    $("#toolbar a.button.anchor-add").click(function(event) {
        $("#toolbar .tab-pane *").hide();
        var p = $('<p class="anchor-insert">URL-adresse: </p>');
        var input = $('<input type="text" name="url">');
        p.append(input);
        var buttons = $('<div class="anchor-buttons btn-group"><button class="btn anchor-add">Sett inn</button><button class="btn anchor-cancel">Avbryt</button></div>');
        buttons.find("button.anchor-add").click(function() {
            var range = selection.getRangeAt(0);
            // Trim the selection for whitespace (actually, just the last char, since that's most common)
            if($(range.endContainer).text().substring(range.endOffset - 1, range.endOffset) == ' ') {
                range.setEnd(range.endContainer, range.endOffset - 1);
            }
            selection.setSingleRange(range);
            var url = $("#toolbar div.formatting input[name='url']").val();
            if(!url.match(/^https?:\/\//)) {
                url = "http://" + url;
            }
            document.execCommand('createLink', false, url);
            reset();
        });
        buttons.find("button.anchor-cancel").click(function() {
            reset();
        });
        function reset() {
            $("#toolbar .formatting p.anchor-insert, #toolbar .formatting div.anchor-buttons").remove();
            $("#toolbar .tab-pane *").show();
        }
        $("#toolbar .tab-pane").append(p, buttons);
    });
    $("#toolbar a.anchor-remove").click(function(event) {
        document.execCommand('unlink', false, null);
    });
    $("#toolbar a.button.bold").click(function(event) {
        document.execCommand('bold', false, null);
    });
    $("#toolbar a.button.italic").click(function(event) {
        document.execCommand('italic', false, null);
    });
    $("#toolbar a.button.underline").click(function(event) {
        document.execCommand('underline', false, null);
    });
    $("#toolbar a.button.ol").click(function(event) {
        document.execCommand('insertorderedlist', false, null);
    });
    $("#toolbar a.button.ul").click(function(event) {
        document.execCommand('insertunorderedlist', false, null);
    });
    $("#toolbar a.button.align-left").click(function(event) {
        document.execCommand('justifyleft', false, null);
    });
    $("#toolbar a.button.align-center").click(function(event) {
        document.execCommand('justifycenter', false, null);
    });
    $("#toolbar a.button.align-right").click(function(event) {
        document.execCommand('justifyright', false, null);
    });
    $("#toolbar a.button.full").click(function(event) {
        document.execCommand('justifyfull', false, null);
    });

    /**
     * Saving the document
     */

    var lastSaveCount = 0;
    var updateSaveCountID;
    function updateSaveCount() {
        lastSaveCount += 1;
        if(lastSaveCount < 30) {
            $("#toolbar span.save-text").html("<i class=\"icon-ok\"></i> Artikkelen er nylig lagret.");
        } else if(lastSaveCount < 60) {
            $("#toolbar span.save-text").html("<i class=\"icon-warning-sign\"></i> Sist lagret for " + lastSaveCount + " sekunder siden.");
        } else {
            $("#toolbar span.save-text").html("<i class=\"icon-warning-sign\"></i> Sist lagret for " + Math.floor(lastSaveCount / 60) + " minutt" + (lastSaveCount >= 120 ? 'er' : '') + " siden.");
        }

        if(lastSaveCount == 60 * 5) {
            $("div.no-save-warning").show();
        }

        if($("#toolbar .save input.autosave:checked").length == 1) {
            var val = $("#toolbar .save input.autosave-frequency").val();
            if(val.match(/^\d+$/) && lastSaveCount > (val * 60)) {
                $("#toolbar .save button.save").click();
                return;
            }
        }
        updateSaveCountID = setTimeout(updateSaveCount, 1000);
    }
    updateSaveCount();

    // Warn when autosave-number is invalid
    $("#toolbar .save input.autosave-frequency").keyup(function() {
        if($(this).val().match(/^\d+$/)) {
            $(this).parents(".control-group").removeClass('error');
        } else {
            $(this).siblings("input.autosave").removeAttr('checked');
            $(this).parents(".control-group").addClass('error');
        }
    });

    $("#toolbar .save button.save").click(function() {
        clearInterval(updateSaveCountID);
        $(this).hide();
        $("div.no-save-warning").hide();
        $("#toolbar span.save-text").text("Lagrer, vennligst vent...");
        enableOverlay();
        disableEditing();
        var rows = [];
        $("article div.row").each(function() {
            var row = {
                id: $(this).attr('data-id'),
                order: $(this).prevAll().length
            };
            rows = rows.concat([row]);
        });
        var columns = [];
        $("article div.column").each(function() {
            var column = {
                id: $(this).attr('data-id'),
                order: $(this).prevAll().length
            };
            columns = columns.concat([column]);
        });
        var contents = [];
        $("article div.html").each(function() {
            var content = {
                id: $(this).attr('data-id'),
                order: $(this).prevAll().length,
                content: $(this).html()
            };
            contents = contents.concat([content]);
        });
        $("article div.image").each(function() {
            var anchor;
            if($(this).find('a').length == 0) {
                anchor = null;
            } else {
                anchor = $(this).find('a').attr('href');
            }
            var image = {
                src: $(this).find('img').attr('src'),
                alt: $(this).find('img').attr('alt'),
                anchor: anchor
            };
            var content = {
                id: $(this).attr('data-id'),
                order: $(this).prevAll().length,
                content: JSON.stringify(image)
            };
            contents = contents.concat([content]);
        });

        $.ajax({
            url: '/sherpa/cms/editor/' + $("article").attr('data-id') + '/',
            type: 'POST',
            data: "rows=" + encodeURIComponent(JSON.stringify(rows)) +
                  "&columns=" + encodeURIComponent(JSON.stringify(columns)) +
                  "&contents=" + encodeURIComponent(JSON.stringify(contents))
        }).done(function(result) {
            lastSaveCount = 0;
        }).fail(function(result) {
            // Todo
            $(document.body).html(result.responseText);
        }).always(function(result) {
            updateSaveCount();
            disableOverlay();
            $("#toolbar button.save").show();
            enableEditing();
        });
    });


    /**
     * Small, logical code snippets
     */

    /* Toggle overlay for the entire site */
    function enableOverlay() {
        $("<div class=\"ui-widget-overlay\"></div>").appendTo('body');
        $("<div class=\"overlay-loader\"><h3>Lagrer, vennligst vent...</h3><p><img src=\"/static/img/ajax-loader-large.gif\" alt=\"Lagrer, vennligst vent...\"></p></div>")
          .appendTo('body');
    }
    function disableOverlay() {
        $(".ui-widget-overlay,.overlay-loader").remove();
    }

    /* Toggle toolbar usage */
    function disableToolbar(displayText, cancelCallback) {
        $("#toolbar .tab-pane *").hide();
        var btn = $('<button class="btn cancel">Avbryt</button>');
        btn.click(enableToolbar);
        btn.click(cancelCallback);
        $("#toolbar .tab-pane").append('<p class="cancel">' + displayText + '</p>', btn);
    }
    function enableToolbar() {
        $("#toolbar .tab-pane .cancel").remove();
        $("#toolbar .tab-pane *").show();
    }

    /* Toggle editing of the actual content */
    function disableEditing() {
        $("article div.html").removeAttr('contenteditable');
        $("article div.image img").off('click focus focusout');
        $("article div.widget").off('click');
    }
    function enableEditing() {
        selectableContent($("article div.html").attr('contenteditable', 'true'));
        changeableImages($("article div.image img"));
        clickableWidgets($("div.widget"));
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
    function setEmpties() {
        $("article .column").each(function() {
            if($(this).children(":not(.insertable)").length == 0) {
                setEmpty($(this));
            }
        });
    }
    function removeEmpties() {
        $("article .column").children("div.empty.well").remove();
    }

    /**
     * Dynamic event handlers
     * These will need to be reapplied for all newly
     * created DOM html elements.
     */

    /* Highlight contenteditables that _are being edited_. */
    function selectableContent(html) {
        html.focus(function() {
            $(this).addClass('selected');
        }).focusout(function() {
            $(this).removeClass('selected');
        }).mouseup(setSelection).keyup(setSelection);
    }

    /* Used by selectableContent */
    function setSelection() {
        selection = rangy.getSelection();
    }

    /* Change image sources upon being clicked. */
    function changeableImages(images) {
        images.parent("a").click(function(e) {
            // For images with anchors, prevent the default link action
            e.preventDefault();
        });
        images.click(function(e) {
            $(this).removeClass('hover');
            currentImage = $(this);
            var anchor = $(this).parent("a").attr('href');
            if(anchor === undefined) {
                anchor = '';
            }
            openImageDialog($(this).attr('src'), anchor, $(this).attr('alt'), saveImage);
            function saveImage(src, anchor, alt) {
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
                currentImage.attr('alt', alt);
                $("#toolbar .save button.save").click();
            }
        });
    }

    function clickableWidgets(widgets) {
        widgets.click(function() {
            var widget = JSON.parse($(this).attr('data-json'));
            widgetBeingEdited = $(this);
            editWidget(widget);
        });
    }

    /* Automatically remove empty content-elements */
    function autoRemoveEmptyContent(html) {
        html.focusout(function() {
            if($(this).text().trim() === "") {
                disableEditing();
                var html = $(this);
                $.ajax({
                    url: '/sherpa/cms/innhold/slett/' + encodeURIComponent(html.attr('data-id')) + '/',
                    type: 'POST'
                }).done(function(result) {
                    if(html.siblings().length == 0) {
                        setEmpty(html.parent());
                    }
                    html.remove();
                }).fail(function(result) {
                    // Todo
                }).always(function(result) {
                    refreshSort();
                    enableEditing();
                });
            }
        });
    }

    /**
     * Major DOM changes.
     * Typically includes an ajax request and,
     * depending on the result, DOM manipulation.
     */

    /* Add content-objects to some column */
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
            var wrapper = $('<div class="' + type + '" data-id="' + result.id + '"></div>').append(result.content);
            if(result.json !== undefined) {
                wrapper.attr('data-json', result.json);
            }
            if(prev.length == 0) {
                parent.prepend(wrapper);
            } else {
                prev.after(wrapper);
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

    /* Editing widgets */

    clickableWidgets($("div.widget"));

    function widgetAdded(wrapper) {
        refreshSort();
        removeEmpties();
        setEmpties();
        clickableWidgets(wrapper);
    }

    function saveWidget(widget, content) {
        $.ajax({
            url: '/sherpa/cms/widget/oppdater/' + widget.attr('data-id') + '/',
            type: 'POST',
            data: 'content=' + encodeURIComponent(content)
        }).done(function(result) {
            result = JSON.parse(result);
            widget.contents().remove();
            widget.append(result.content);
            widget.attr('data-json', result.json);
        }).always(function() {
            disableOverlay();
        });
    }

    // Save quote-widget
    $("div.dialog.widget-edit.quote button.save").click(function() {
        var content = JSON.stringify({
            widget: "quote",
            quote: $("div.dialog.widget-edit.quote textarea[name='quote']").val(),
            author: $("div.dialog.widget-edit.quote input[name='author']").val()
        });
        if(widgetBeingEdited !== undefined) {
            $("div.dialog.widget-edit.quote").dialog('close');
            enableOverlay();
            saveWidget(widgetBeingEdited, content);
        } else {
            $(this).parents(".dialog").dialog('close');
            addContent(widgetPosition.prev, widgetPosition.parent, widgetPosition.column,
                widgetPosition.order, content, 'widget', widgetAdded);
        }
    });

    function editWidget(widget) {
        if(widget.widget == 'quote') {
            $("div.dialog.widget-edit.quote textarea[name='quote']").val(widget.quote);
            $("div.dialog.widget-edit.quote input[name='author']").val(widget.author);
            $("div.dialog.widget-edit.quote").dialog('open');
        }
    }

});
